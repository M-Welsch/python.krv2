from PIL import ImageDraw
from PIL.Image import Image
from signalslot import Signal


class Hmi:
    enc0 = Signal(args=["amount"])
    enc0_sw = Signal()
    enc1 = Signal(args=["amount"])
    enc1_sw = Signal()
    button = Signal(args=["name"])

    def start(self):
        pass

    @property
    def dis0(self) -> ImageDraw.Draw:
        return ImageDraw.Draw(Image())

    @property
    def dis1(self) -> ImageDraw.Draw:
        return ImageDraw.Draw(Image())
