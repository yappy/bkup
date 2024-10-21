# bkup

[![Client Python Test](https://github.com/yappy/bkup/actions/workflows/python.yaml/badge.svg)](https://github.com/yappy/bkup/actions/workflows/python.yaml)
[![Server Rust Test](https://github.com/yappy/bkup/actions/workflows/rust.yaml/badge.svg)](https://github.com/yappy/bkup/actions/workflows/rust.yaml)
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
WSL 内から Windows のファイルを圧縮のために読み取るのはパフォーマンス上の観点から
非推奨なので、後述の `runaswin.py` との併用を推奨します。

#### sync

ディレクトリツリーのコピー (同期) を行います。
展開せずにすぐに使えるバックアップ、およびアーカイブ前にバックアップ対象を
一か所に固める用。
Unix / Windows で使用ツールを自動スイッチします。

Requirements:

* Unix
  * `rsync`
    * e.g. `sudo apt install rsync`
* Windows
  * `Robocopy`
    * 最初から入っているはず

##### rsync の注意

`--src` に渡されたパラメータ (複数指定可) はそのまま rsync に渡されます。
対象がディレクトリの場合、最後に `/` がつくかつかないかで意味が変わります。

* `path/to/dir`: そのディレクトリを転送する。
* `path/to/dir/`: そのディレクトリの中身を転送する。

特に複数の `--src` を指定する場合、前者をお勧めします。

#### archive

ディレクトリ1つをユーザ/マシン名や日時の入ったいい感じの名前の圧縮ファイルに
アーカイブします。
Unix / Windows で使用ツールを自動スイッチします。

Requirements:

* Unix
  * `pbzip2`
    * Parallel version of bzip2
    * e.g. `sudo apt install pbzip2`
* Windows
  * `7z`
    * e.g. `winget install 7zip`

可能ならば追加インストールなし、同じファイルフォーマットにしたかったが、
熟考の結果こうなっています。

* `tar` + `gz` or `bz2` or `xz` は owner, permission, symlink を格納でき
  UNIX システムのバックアップに非常に適している。
* ファイルサイズが大きいので並列化をかけないとコアと時間が大幅に損。

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
