from time import sleep

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
        raise RuntimeError("implement start-method in the respective hmi subclass!")

    @property
    def dis0(self) -> ImageDraw.Draw:
        return ImageDraw.Draw(Image())

    @property
    def dis1(self) -> ImageDraw.Draw:
        return ImageDraw.Draw(Image())

    def show_on_display(self, display_index: int, image: Image):
        raise RuntimeError("implement start-method in the respective hmi subclass!")
