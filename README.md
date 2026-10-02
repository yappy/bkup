# bkup

[![Client Python Test](https://github.com/yappy/bkup/actions/workflows/python.yaml/badge.svg)](https://github.com/yappy/bkup/actions/workflows/python.yaml)
[![Shell Script Lint](https://github.com/yappy/bkup/actions/workflows/sh.yaml/badge.svg)](https://github.com/yappy/bkup/actions/workflows/sh.yaml)

Backup manager and tools

## Backup Script

`src/bkup.py`

[Tech Note](note/technote.md)

### Requirements

* Linux
  * python3
    * 多分最初からある。
  * rsync
    * `sudo apt install rsync`
  * pbzip2
    * `sudo apt install pbzip2`
    * マルチスレッド版 .bz2 圧縮。さすがにマルチコアだと速さが違う。
* Windows
  * winget
    * <https://learn.microsoft.com/ja-jp/windows/package-manager/winget/>
    * 無くてもいいけどあると楽。
    * 無いなら以下は公式サイトからダウンロードしてインストール。
  * 7-Zip
    * `winget install 7zip.7zip`
    * やはり圧縮率と速さがいい。
  * python 3.x
    * WSL 上の Linux Python を使うなら不要。
    * `winget search python` で探して `winget install Python.Python.3.12`
      のように入れる。
    * msstore ではなく winget の方。
    * 3.10 くらい以降推奨。
    * 自動テストの結果参照。
    * <https://github.com/yappy/bkup/actions>

### bkup.py

クライアントツール群のフロントエンド。

```sh
$ ./src/bkup.py
./src/bkup.py SUBCMD [args...]
Subcommands
* sync
    Make a backup copy of directory
* clean
    Clean old archive files
* archive
    Compress directory and make an archive file
* dockervol
    Compress Docker volumes and make an archive file
* upload
    Copy the latest archive file to a remote host by rsync
* cloudsetup
    Setup rclone tool
* cloudclean
    Clean old archive files on the cloud storage
* cloud
    Copy the latest archive file to the cloud storage
```

#### sync

```sh
$ ./src/bkup.py sync -h
usage: sync [-h] [--src SRC [SRC ...]] --dst DST [--exclude [EXCLUDE ...]]
            [--exclude-from [EXCLUDE_FROM ...]]
            [--exclude-file [EXCLUDE_FILE ...]]
            [--exclude-dir [EXCLUDE_DIR ...]] [--dry-run] [--force]

Make a copy of file tree (Linux: rsync, Windows: robocopy)

options:
  -h, --help            show this help message and exit
  --src, -s SRC [SRC ...]
                        backup source dir (rsync: dir/ means all entries in
                        the dir will be copied. dir means dir directory will
                        be copied)
  --dst, -d DST         backup destination dir
  --exclude [EXCLUDE ...]
                        exclude patterns (rsync)
  --exclude-from [EXCLUDE_FROM ...]
                        exclude list files (rsync)
  --exclude-file [EXCLUDE_FILE ...]
                        exclude files (Robocopy)
  --exclude-dir [EXCLUDE_DIR ...]
                        exclude dirs (Robocopy)
  --dry-run, -n         dry run
  --force, -f           run without confirmation

Make sure of what will happen because sync operation may destruct the dest
dir.
```

ディレクトリツリーのコピー (同期) を行います。
SRC (複数) を DST (単独) 以下にコピーします。

展開せずにすぐに使えるバックアップ、およびアーカイブ前にバックアップ対象を
一か所に固めるためのコマンドです。

Unix / Windows / WSL で使用ツールを自動スイッチします。

##### rsync の注意

`--src` に渡されたパラメータ (複数指定可) はそのまま rsync に渡されます。
対象がディレクトリの場合、最後に `/` がつくかつかないかで意味が変わります。

* `path/to/dir`: そのディレクトリを転送する。
* `path/to/dir/`: そのディレクトリの中身を転送する。

特に複数の `--src` を指定する場合、前者をお勧めします。

#### archive

```sh
$ ./src/bkup.py archive -h
usage: archive [-h] --src SRC --dst DST [--tag TAG] [--dry-run]

Archive and compress a directory (Linux: tar.bz2, Windows: 7z)

options:
  -h, --help     show this help message and exit
  --src, -s SRC  backup source dir
  --dst, -d DST  backup destination dir
  --tag, -t TAG  tag string for archive file name (default: user_name)
  --dry-run, -n  dry run
```

SRC ディレクトリ (1つ) をユーザ/マシン名や日時の入ったいい感じの名前の圧縮ファイルに
アーカイブします。
Unix / Windows で使用ツールを自動スイッチします。

#### clean

```sh
$ ./src/bkup.py clean -h
usage: clean [-h] --dst DST [--dry-run] [--keep-count KEEP_COUNT]
             [--keep-days KEEP_DAYS]

Clean old archive files

options:
  -h, --help            show this help message and exit
  --dst, -d DST         archive files dir
  --dry-run, -n         dry run
  --keep-count KEEP_COUNT
                        keep the latest N files
  --keep-days KEEP_DAYS
                        keep files not expired

A file will be deleted only if it is out of --keep-count AND out of --keep-
days
```

archive で生成されたアーカイブファイルのうち、古いものを削除します。
archive と同じ DST を指定してください。
KEEP_COUNT と KEEP_DAYS の両方から外れたファイルが削除されます。

#### upload

```sh
$ ./src/bkup.py upload -h
usage: upload [-h] --src SRC --dst DST [--ssh SSH] [--dry-run]

Copy the latest archive file to a remote host by rsync

options:
  -h, --help     show this help message and exit
  --src, -s SRC  archive dir
  --dst, -d DST  rsync destination (user@host:dir)
  --ssh SSH      ssh command line (e.g. --ssh "ssh -p 12345")
  --dry-run, -n  dry run
```

archive で生成されたファイルの中で最も新しいものを rsync でリモートに転送します。

SRC には archive で指定していた DST を指定してください。

DST にはリモートディレクトリを rsync で使えるような形式で指定してください。
`user@host:path/to/dir` のような形になります。
ローカルのパスも指定可能です。

#### dockervol

```sh
$ ./src/bkup.py dockervol -h
usage: dockervol [-h] --project PROJECT --volume VOLUME --dst DST [--dry-run]

Archive and compress docker volumes (tar.bz2)

options:
  -h, --help            show this help message and exit
  --project, -p PROJECT
                        Docker compose project name
  --volume, -v VOLUME   Docker volume name to back up (excluding project name)
                        (multiple OK)
  --dst, -d DST         backup destination dir
  --dry-run, -n         dry run
```

Docker Compose プロジェクトの volume をコンテナ経由で tar.bz2 にアーカイブします。
`--volume` は複数回指定できます。

#### cloudsetup

```sh
$ ./src/bkup.py cloudsetup -h
usage: cloudsetup [-h]

Setup rclone tool

options:
  -h, --help  show this help message and exit

This is rclone wrapper
```

rclone のセットアップ補助コマンドです。

#### cloudclean

```sh
$ ./src/bkup.py cloudclean -h
usage: cloudclean [-h] --remote REMOTE [--dst DST] [--dry-run]
                  [--keep-count KEEP_COUNT] [--keep-days KEEP_DAYS]

Copy the latest archive file to a cloud storage

options:
  -h, --help            show this help message and exit
  --remote, -r REMOTE   backup destination remote name
  --dst, -d DST         backup destination dir on remote (remote:HERE)
  --dry-run, -n         dry run
  --keep-count KEEP_COUNT
                        keep the latest N files
  --keep-days KEEP_DAYS
                        keep files not expired

This is rclone wrapper
```

rclone のリモートストレージ上にある古いアーカイブファイルを削除します。
KEEP_COUNT と KEEP_DAYS の両方から外れたファイルが削除されます。

#### cloud

```sh
$ ./src/bkup.py cloud -h
usage: cloud [-h] --src SRC --remote REMOTE [--dst DST] [--progress]
             [--dry-run]

Copy the latest archive file to a cloud storage

options:
  -h, --help           show this help message and exit
  --src, -s SRC        archive dir
  --remote, -r REMOTE  backup destination remote name
  --dst, -d DST        backup destination dir on remote (remote:HERE)
  --progress, -P       show progress
  --dry-run, -n        dry run

This is rclone wrapper
```

archive で生成されたファイルの中で最も新しいものを rclone でクラウドストレージに転送します。
SRC には archive で指定していた DST を指定してください。

### runaswin.py

WSL 内から Windows python を呼び出すラッパです。
WSL からの `.exe` 呼び出しで十分な場合は不要。

### Test

```sh
# python3 -m unittest discover client
./test.sh

# Launch windows test from WSL
# python3 ./client/runaswin.py -m unittest discover client
./win_test_from_wsl.sh
```

## scripts

実践的な使用例は `scripts` 以下にあります。

## Lint

```sh
# shell script
./shellcheck.sh
# python
./flake8.sh
```
