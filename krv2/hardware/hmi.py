import json
import logging
from pathlib import Path

from luma.core.render import canvas
from PIL import Image, ImageDraw, ImageFont
from signalslot import Signal

from krv2.hardware.displays import Displays
from krv2.hardware.hid import HumanInterfaceDevice

LOG = logging.getLogger(Path(__file__).name)


class HumanMachineInterface:
    def __init__(self, pin_interface):
        self._hid = HumanInterfaceDevice(pin_interface)
        self._hid.start()
        displays = Displays()
        self._nav_display: ImageDraw.Draw = displays.dis1
        self._connect_signals()
        self.on_refresh_nav_display()

    @property
    def nav(self):
        return self._nav

    def _connect_signals(self):
        self._hid.enc0_value_changed.connect(self._nav.on_env_val_changed)
        # self._nav.refresh_nav_display.connect(self.on_refresh_nav_display)
        self._hid.enc0_sw_pressed.connect(self._nav.on_enc0_pressed)
        self._hid.button_back_pressed.connect(self._nav.on_button_back_pressed)

    def on_refresh_nav_display(self, **kwargs):
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        with canvas(self._nav_display) as nav_display:
            posy = 0
            for line in self._nav.current_slice_of_dir_content:
                line = str(line)
                if line == self._nav.cursor_text:
                    self._place_cursor(nav_display, posy)
                nav_display.text((5, posy), line, fill="white", font=fnt)
                posy += 11

    def _place_cursor(self, nav_display, posy):
        nav_display.rectangle(xy=[0, posy + 4, 2, posy + 6], fill="white")
