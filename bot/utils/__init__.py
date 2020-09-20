from .utils import CommonUtils
from .manual_screenshot import ManualScreenshot
from .sample import Sample
from .trim import Trim
from .screenshot import Screenshot
from .base import BaseUtils


class Methods(ManualScreenshot, Sample, Trim, Screenshot):
    pass


class Utilities(BaseUtils, CommonUtils, Methods):
    pass
