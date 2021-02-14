import asyncio
import logging
from collections import defaultdict
from contextlib import asynccontextmanager

from async_timeout import timeout

from bot.config import Config


logger = logging.getLogger(__name__)


class TooMuchProcess(Exception):
    pass


class Worker:
    def __init__(self):
        self.worker_count = Config.WORKER_COUNT
        self.user_process_count = defaultdict(lambda: 0)
        self.queue = asyncio.Queue()

    async def start(self):
        for _ in range(self.worker_count):
            asyncio.create_task(self._worker())
        logger.debug("Started %s workers", self.worker_count)

    async def stop(self):
        logger.debug("Stopping workers")
        for _ in range(self.worker_count):
            self.new_task(None)
        await self.queue.join()
        logger.debug("Stopped workers")

    def new_task(self, task):
        self.queue.put_nowait(task)

    @asynccontextmanager
    async def count_user_process(self, chat_id):
        if self.user_process_count[chat_id] >= Config.MAX_PROCESSES_PER_USER:
            raise TooMuchProcess

        self.user_process_count[chat_id] += 1
        try:
            yield
        finally:
            self.user_process_count[chat_id] -= 1

    async def _worker(self):
        while True:
            task = await self.queue.get()
            try:
                if task is None:
                    break

                chat_id, process_factory = task
                handler = process_factory.get_handler()
                try:
                    async with self.count_user_process(chat_id), timeout(
                        Config.TIMEOUT
                    ):
                        await handler.process()
                except (asyncio.TimeoutError, asyncio.CancelledError):
                    await handler.cancelled()
                except TooMuchProcess:
                    await asyncio.sleep(10)
                    self.new_task((chat_id, process_factory))

            except Exception as e:
                logger.error(e, exc_info=True)
            finally:
                self.queue.task_done()
