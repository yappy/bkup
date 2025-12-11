from . import sync, archive, clean, upload, cloudsetup, cloud

command_table = [
    (sync.main, "sync", "Make a backup copy of directory"),
    (clean.main, "clean", "Clean old archive files"),
    (archive.main, "archive", "Compress directory and make a archive file"),
    (upload.main, "upload", "Copy the latest archive file to a remote host by rsync"),
    (cloudsetup.main, "cloudsetup", "Setup rclone tool"),
    (cloud.main, "cloud", "Copy the latest archive file to a cloud storage"),
]
