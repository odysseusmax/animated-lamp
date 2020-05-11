import os
from pathlib import Path

class Config:
    
    API_ID = int(os.environ.get('API_ID'))
    API_HASH = os.environ.get('API_HASH')
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    SESSION_NAME = os.environ.get('SESSION_NAME')
    LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL'))
    DATABASE_URL = os.environ.get('DATABASE_URL')
    AUTH_USERS = [int(i) for i in os.environ.get('AUTH_USERS', '').split(' ')]
    MAX_PROCESSES_PER_USER = int(os.environ.get('MAX_PROCESSES_PER_USER', 2))
    MAX_TRIM_DURATION = int(os.environ.get('MAX_TRIM_DURATION', 600))
    TRACK_CHANNEL = int(os.environ.get('TRACK_CHANNEL', False))
    SLOW_SPEED_DELAY = int(os.environ.get('SLOW_SPEED_DELAY', 15))
    HOST = os.environ.get('HOST', '')
    
    SCRST_OP_FLDR = Path('screenshots/')
    SMPL_OP_FLDR = Path('samples/')
    THUMB_OP_FLDR = Path('thumbnails/')
    COLORS = ['white', 'black', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'brown', 'gold', 'silver', 'pink']
    FONT_SIZES_NAME = ['Small', 'Medium', 'Large']
    FONT_SIZES = [30, 40, 50]
