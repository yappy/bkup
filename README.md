# bkup

[![Client Python Test](https://github.com/yappy/bkup/actions/workflows/python.yaml/badge.svg)](https://github.com/yappy/bkup/actions/workflows/python.yaml)
[![Shell Script Lint](https://github.com/yappy/bkup/actions/workflows/sh.yaml/badge.svg)](https://github.com/yappy/bkup/actions/workflows/sh.yaml)

Backup manager and tools

## client

[Tech Note](note/client.md)

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
$ ./bkup.py
./bkup.py SUBCMD [args...]
Subcommands
* sync
    Make a backup copy of directory
* clean
    Clean old archive files
* archive
    Compress directory and make a archive file
* upload
    Copy the latest archive file to a remote host by rsync
```

#### sync

```sh
$ ./bkup.py sync -h
usage: sync [-h] [--src SRC [SRC ...]] --dst DST [--exclude EXCLUDE] [--exclude-file [EXCLUDE_FILE ...]]
            [--exclude-dir [EXCLUDE_DIR ...]] [--dry-run] [--force]

Make a copy of file tree (Linux: rsync, Windows: robocopy)
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
$ ./bkup.py archive -h
usage: archive [-h] --src SRC --dst DST [--dry-run]

Archive and compress a directory (Linux: tar.bz2, Windows: 7z)
```

SRC ディレクトリ (1つ) をユーザ/マシン名や日時の入ったいい感じの名前の圧縮ファイルに
アーカイブします。
Unix / Windows で使用ツールを自動スイッチします。

#### clean

```sh
$ ./bkup.py clean -h
usage: clean [-h] --dst DST [--dry_run] [--keep-count KEEP_COUNT] [--keep-days KEEP_DAYS]

Clean old archive files
```

archive で生成されたアーカイブファイルのうち、古いものを削除します。
archive と同じ DST を指定してください。
KEEP_COUNT と KEEP_DAYS の両方から外れたファイルが削除されます。

#### upload

```sh
$ ./bkup.py upload -h
usage: upload [-h] --src SRC --dst DST [--ssh SSH] [--dry-run]

Copy the latest archive file to a remote host by rsync
```

archive で生成されたファイルの中で最も新しいものを rsync でリモートに転送します。

SRC には archive で指定していた DST を指定してください。

DST にはリモートディレクトリを rsync で使えるような形式で指定してください。
`user@host:path/to/dir` のような形になります。
ローカルのパスも指定可能です。

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

## server

[Tech Note](note/server.md)

### server - Build

```sh
cargo build --release
```

### server - Run

```sh
cargo run --release -- --help
$ cargo run --release -- --help

Backup files maintenance tool

Usage: bkupserver [OPTIONS]

Options:
      --log-level <LEVEL>    [default: INFO]
      --log-file <FILE>      [default: bkupsv.log]
  -t, --task-all             Enable all the tasks
      --task-repo            Enable repository clean task
      --task-inbox           Enable inbox > repository move task
      --task-sync            Enable sync with cloud storage task
      --inbox-dir <DIR>      Inbox directory path [default: /tmp/inbox]
      --repo-dir <DIR>       Repository directory path [default: /tmp/repo]
      --sync-dir <DIR>       Cloud sync directory path [default: /tmp/sync]
  -c, --config-file <FILE>   Read parameters from TOML file (other command line parameters will be ignored) [default: ]
  -g, --gen-config <FILE>    Generate a config file template and exit [default: ]
```

* 起動パラメータ関連
  * `--gen-config`
    * デフォルト設定からなるコンフィグファイルを出力します。
  * `--config-file`
    * コマンドラインの代わりにコンフィグファイルに書かれた設定を使用します。
* ログ関連
  * `--log-level`
    * TRACE, DEBUG, INFO, WARN, ERROR
  * `--log-file`
* ディレクトリ
  * `--inbox-dir`
    * クライアントが rsync 等でファイルを置く想定のディレクトリです。
  * `--repo-dir`
    * 管理中のアーカイブファイルが置かれるディレクトリです。
  * `--sync-dir`
    * クラウドストレージと同期するためのディレクトリです。

### server - Format and Lint

```sh
cargo fmt --check
cargo clippy
```

### server - Test

```sh
cargo test
```

## scripts

実戦的な使用例。

### scripts - Lint

shellcheck

```sh
./scripts/lint.sh
```
