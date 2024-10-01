from . import sync, archive, clean, upload

command_table = [
    (sync.main, "sync", "Make a backup copy of directory"),
    (clean.main, "clean", "Compress directory and make a archive file"),
    (archive.main, "archive", "Compress directory and make a archive file"),
    (upload.main, "upload", "Compress directory and make a archive file"),
]
