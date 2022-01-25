import logging
from pathlib import Path
from subprocess import run, PIPE
from threading import Thread


LOG = logging.getLogger(__name__)


class SyncError(Exception): pass


class Synchronisation(Thread):
    def __init__(self, cfg_sync: dict) -> None:
        super().__init__()
        self._cfg_sync = cfg_sync
        self._status = {}

    @property
    def status(self) -> dict:
        return self._status

    def run(self) -> None:
        self.mount_remote_music_collection()
        self.mirror_music_collection()
        self.sync_mishmash()

    def mount_remote_music_collection(self) -> None:
        if not Path("/etc/win-credentials").exists():
            raise SyncError("/etc/win-credentials doesn't exist.")
        cmd = "sudo mount -a"
        p = run(cmd.split(), stdout=PIPE, stderr=PIPE)
        if p.stderr:
            LOG.error(p.stderr)

    def mirror_music_collection(self) -> None:
        local_music_collection_location = self._cfg_sync["local_music_collection"]["location"]
        remote_music_collection_location = self._cfg_sync["remote_music_collection"]["location"]
        cmd = "rsync ..."
        run(cmd)

    def sync_mishmash(self) -> None:
        music_collection_location = self._cfg_sync["music_collection_location"]
        cmd = f"mishmash {music_collection_location}"
        run(cmd)