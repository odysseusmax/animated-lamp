import datetime

import motor.motor_asyncio

from config import Config

class Database:
    
    def __init__(self, uri):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[Config.SESSION_NAME]
        self.col = self.db.users
    
    
    def new_user(self, id):
        return dict(
            id = id,
            join_date = datetime.date.today().isoformat(),
            as_file=False,
            watermark_text='',
            sample_duration=30,
            watermark_color=0
        )
    
    
    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)
    
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return True if user else False
    
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    
    async def is_as_file(self, id):
        user = await self.col.find_one({'id':int(id)})
        return user.get('as_file', False)
    
    
    async def update_as_file(self, id, as_file):
        await self.col.update_one({'id': id}, {'$set': {'as_file': as_file}})
    
    
    async def update_watermark_text(self, id, watermark_text=''):
        await self.col.update_one({'id': id}, {'$set': {'watermark_text': watermark_text}})
    
    
    async def update_sample_duration(self, id, sample_duration):
        await self.col.update_one({'id': id}, {'$set': {'sample_duration': sample_duration}})
    
    
    async def update_watermark_color(self, id, watermark_color):
        await self.col.update_one({'id': id}, {'$set': {'watermark_color': watermark_color}})
    
    
    async def get_watermark_text(self, id):
        user = await self.col.find_one({'id':int(id)})
        return user.get('watermark_text', '')
    
    
    async def get_sample_duration(self, id):
        user = await self.col.find_one({'id':int(id)})
        return user.get('sample_duration', 30)
    
    
    async def get_watermark_color(self, id):
        user = await self.col.find_one({'id':int(id)})
        return user.get('watermark_color', 0)
