import os

class Config:
    
    API_ID = int(os.environ.get('API_ID'))
    API_HASH = os.environ.get('API_HASH')
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    SESSION_NAME = os.environ.get('SESSION_NAME')
    USER_SESSION_STRING = os.environ.get('USER_SESSION_STRING')
    MIDDLE_MAN = int(os.environ.get('MIDDLE_MAN'))
    LINK_GEN_BOT = os.environ.get('LINK_GEN_BOT')
