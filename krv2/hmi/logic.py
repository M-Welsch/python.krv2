from enum import Enum

from luma.core.render import canvas
from PIL import Image, ImageDraw, ImageFont

from krv2.hmi.hmi import Hmi
from krv2.music_collection import Database, Navigation


class States(Enum):
    mode_selection = 0
    navigation = 1


class Logic:
    def __init__(self, hmi: Hmi, cfg_logic: dict) -> None:
        self._hmi = hmi
        self._db = Database(cfg_db=cfg_logic["database"])
        self._navigation = Navigation(cfg_nav=cfg_logic["navigation"], db=self._db)
        self._state = States.navigation
        self.connect_signals()
        self._hmi.start()
        self._dis0 = self._hmi.dis0
        self.visualize_list_slice()

    def connect_signals(self) -> None:
        self._hmi.enc0.connect(self.on_enc_movement)
        self._hmi.enc0_sw.connect(self.on_enc0_sw_pressed)
        self._hmi.button.connect(self.on_button_pressed)

    def on_enc_movement(self, amount, **kwargs):  # type: ignore
        if self._state == States.navigation:
            if amount < 0:
                self._navigation.up()
            elif amount > 0:
                self._navigation.down()

    def on_enc0_sw_pressed(self, **kwargs):  # type: ignore
        if self._state == States.navigation:
            self._navigation.into()

    def on_button_pressed(self, name, **kwargs):  # type: ignore
        if self._state == States.navigation:
            if name == "button_back":
                self._navigation.out()

    def visualize_list_slice(self) -> None:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        with canvas(self._dis0) as nav_display:
            posy = 0
            for line in self._navigation.current_slice:
                # if line == self._nav.cursor_text:
                #    self._place_cursor(nav_display, posy)
                nav_display.text((5, posy), line, fill="white", font=fnt)
                posy += 11

    def _place_cursor(self, nav_display, posy):
        nav_display.rectangle(xy=[0, posy + 4, 2, posy + 6], fill="white")
