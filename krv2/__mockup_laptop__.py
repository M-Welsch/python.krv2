from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from krv2.music_player.vlc_wrapper import VlcWrapper
from krv2.hardware.hmi import Navigation


class MockupLaptop:
    def __init__(self):
        self._vlc = VlcWrapper()
        self._nav = Navigation(DisplayMockup().display)

    def start(self):
        exit_flag = False
        try:
            while not exit_flag:
                keyp = input("Key:")
                if keyp == "p":
                    print("pause-play")
                    self._vlc.pause_play()
                if keyp == "n":
                    print("next")
                    self._vlc.next()
                if keyp == "q":
                    exit_flag = True
                if keyp == "s":
                    print("toggle shuffle")
                    self._vlc.toggle_shuffle()
                if keyp == "a":
                    print("adding music files")
                    self._vlc.setup_list_player([
                        Path("/home/max/Music/Avantasia/Moonglow (Ltd. Ed.)/04.The Raven Child.mp3"),
                        Path("/home/max/Music/Avantasia/Ghostlights/02 Let The Storm Descend Upon You.mp3"),
                        Path("/home/max/Music/Avantasia/Ghostlights/06 Draconian Love.mp3")
                    ])
                if keyp == "i":
                    print(self._vlc.get_track_info())

        except KeyboardInterrupt:
            pass
        print("Exiting")


class DisplayMockup:
    def __init__(self):
        # create an image
        out = Image.new("RGB", (150, 100), (55, 55, 55))

        # get a font
        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 40)
        # get a drawing context
        self.d = ImageDraw.Draw(out)

        # draw multiline text
        #self.d.multiline_text((10, 10), "Hello\nWorld", font=fnt, fill=(0, 0, 0))

        out.show()

    @property
    def display(self):
        return self.d


mockup_laptop = MockupLaptop()
mockup_laptop.start()
