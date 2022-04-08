from pathlib import Path
from random import randint

import vlc


class VlcWrapper:
    def __init__(self) -> None:
        self._instance = vlc.Instance(["--no-xlib"])
        self._list_player = self._instance.media_list_player_new()
        self._player = self._list_player.get_media_player()
        self._shuffle = False
        self._media_list = []

    def setup_list_player(self, file_list: list) -> None:
        _media_files = [self._instance.media_new(file) for file in file_list]
        self._media_list = self._instance.media_list_new(_media_files)
        self._list_player.set_media_list(self._media_list)

    def repeat_on(self) -> None:
        self._list_player.set_playback_mode(vlc.PlaybackMode.loop)

    def repeat_off(self) -> None:
        self._list_player.set_playback_mode(vlc.PlaybackMode.default)

    def toggle_shuffle(self) -> None:
        self._shuffle = not self._shuffle

    def shuffle_on(self) -> None:
        self._shuffle = True

    def shuffle_off(self) -> None:
        self._shuffle = False

    def pause_play(self) -> None:
        if (
            self._list_player.get_state() == vlc.State.NothingSpecial
            or self._list_player.get_state() == vlc.State.Paused
        ):
            self._list_player.play()
        else:
            self._list_player.pause()

    def next(self) -> None:
        if self._shuffle:
            index = randint(0, len(self._media_list))
            self._list_player.play_item_at_index(index)
        else:
            self._list_player.next()

    def get_track_info(self) -> dict:
        media = self._player.get_media()
        return {
            "Title": media.get_meta(0),
            "Artist": media.get_meta(1),
            "Genre": media.get_meta(2),
            "Album": media.get_meta(4),
            "Track": media.get_meta(5),
            "Year": media.get_meta(8),
        }

    def get_position(self) -> float:
        return self._player.get_position()
