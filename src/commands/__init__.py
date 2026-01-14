from . import sync, clean, archive, dockervol, upload
from . import cloudsetup, cloudclean, cloud

command_table = [
    (sync.main, "sync", "Make a backup copy of directory"),
    (clean.main, "clean", "Clean old archive files"),
    (archive.main, "archive", "Compress directory and make an archive file"),
    (dockervol.main, "dockervol", "Compress Docker volumes and make an archive file"),
    (upload.main, "upload", "Copy the latest archive file to a remote host by rsync"),
    (cloudsetup.main, "cloudsetup", "Setup rclone tool"),
    (cloudclean.main, "cloudclean", "Clean old archive files on the cloud storage"),
    (cloud.main, "cloud", "Copy the latest archive file to the cloud storage"),
]
