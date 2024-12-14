from . import sync, archive, clean, upload

command_table = [
    (sync.main, "sync", "Make a backup copy of directory"),
    (clean.main, "clean", "Clean old archive files"),
    (archive.main, "archive", "Compress directory and make a archive file"),
    (upload.main, "upload", "Copy the latest archive file to a remote host by rsync"),
]
