from bot.utils import ProcessTypes
from .sample import SampleVideoProcess
from .manual_screenshot import ManualScreenshotsProcess
from .trim import TrimVideoProcess
from .screenshot import ScreenshotsProcess
from .mediainfo import MediaInfoProcess


class ProcessFactory:
    def __init__(self, process_type, client, input_message, reply_message=None):
        self.process_type = process_type
        self.client = client
        self.input_message = input_message
        if (
            process_type in [ProcessTypes.TRIM_VIDEO, ProcessTypes.MANNUAL_SCREENSHOTS]
            and not reply_message
        ):
            raise ValueError("reply_message should not be empty for this process type")
        self.reply_message = reply_message

    def get_handler(self):
        if self.process_type == ProcessTypes.SAMPLE_VIDEO:
            return SampleVideoProcess(self.client, self.input_message)
        elif self.process_type == ProcessTypes.MANNUAL_SCREENSHOTS:
            return ManualScreenshotsProcess(self.client, self.input_message, self.reply_message)
        elif self.process_type == ProcessTypes.TRIM_VIDEO:
            return TrimVideoProcess(self.client, self.input_message, self.reply_message)
        elif self.process_type == ProcessTypes.SCREENSHOTS:
            return ScreenshotsProcess(self.client, self.input_message)
        elif self.process_type == ProcessTypes.MEDIAINFO:
            return MediaInfoProcess(self.client, self.input_message)
        else:
            raise NotImplementedError
