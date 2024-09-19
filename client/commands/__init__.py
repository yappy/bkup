from . import sync, archive

command_table = [
    (sync.main, "sync", "Make a backup copy of directory"),
    (archive.main, "archive", "Compress directory and make a archive file"),
]
