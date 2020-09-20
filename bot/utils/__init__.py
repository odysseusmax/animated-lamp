from .utils import CommonUtils
from .manual_screenshot import ManualScreenshot
from .sample import Sample
from .trim import Trim
from .screenshot import Screenshot


class Methods(ManualScreenshot, Sample, Trim, Screenshot):
    pass


class Utilities(CommonUtils, Methods):
    pass
