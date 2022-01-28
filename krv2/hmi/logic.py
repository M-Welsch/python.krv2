from enum import Enum

from PIL import Image, ImageDraw, ImageFont

from krv2.hmi.hmi import Hmi
from krv2.music_collection import Database, Navigation
from krv2.hardware.port_expander import Buttons


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
        self.visualize_list_slice()
        self._button_mapping = {
            States.navigation: {
                Buttons.enc0_sw: self._navigation.into,
                Buttons.enc1_sw: lambda: None,
                Buttons.button_back: self._navigation.out,
                Buttons.button_pause_play: lambda: None,
                Buttons.button_prev_song: lambda: None,
                Buttons.button_next_song: lambda: None,
                Buttons.button_shuffle_repeat: lambda: None,
                Buttons.button_spare: lambda: None,
                Buttons.button_next_source: lambda: None,
                Buttons.dummy: lambda: None,
                Buttons.button_exit: lambda: None,
            }
        }
        self._hmi.start()

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

    # Fixme: include this into on_Button_pressed below!!!
    def on_enc0_sw_pressed(self, **kwargs):  # type: ignore
        if self._state == States.navigation:
            self._navigation.into()

    def on_button_pressed(self, name, **kwargs):  # type: ignore
        name: Buttons
        self._button_mapping[self._state][name]()
        print(f"Button {name} pressed")

    def visualize_list_slice(self) -> None:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        display_content = Image.new(mode="1", size=(128, 64), color=0)
        canvas = ImageDraw.Draw(display_content)
        posy = 0
        for line in self._navigation.current_slice:
            # if line == self._nav.cursor_text:
            #    self._place_cursor(nav_display, posy)
            canvas.text((5, posy), line, fill="white", font=fnt)
            posy += 11
        self._hmi.show_on_display(0, display_content)

    def _place_cursor(self, nav_display, posy):
        nav_display.rectangle(xy=[0, posy + 4, 2, posy + 6], fill="white")
