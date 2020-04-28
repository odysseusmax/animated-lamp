import os
from pathlib import Path

class Config:
    
    API_ID = int(os.environ.get('API_ID'))
    API_HASH = os.environ.get('API_HASH')
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    SESSION_NAME = os.environ.get('SESSION_NAME')
    USER_SESSION_STRING = os.environ.get('USER_SESSION_STRING')
    MIDDLE_MAN = int(os.environ.get('MIDDLE_MAN'))
    LINK_GEN_BOT = os.environ.get('LINK_GEN_BOT')
    LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL'))
    DATABASE_URL = os.environ.get('DATABASE_URL')
    AUTH_USERS = [int(i) for i in os.environ.get('AUTH_USERS', '').split(' ')]
    
    SCRST_OP_FLDR = Path('screenshots/')
    SMPL_OP_FLDR = Path('samples/')
