# bkup

[![Client Script Test](https://github.com/yappy/bkup/actions/workflows/python.yaml/badge.svg)](https://github.com/yappy/bkup/actions/workflows/python.yaml)

Backup manager and tools

## client

[Tech Note](note/client.md)

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
  * `Robocopy`
    * 最初から入っているはず

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

Requirements:

* `py.exe` is available.
  * You can install by e.g. `winget install Python.Python.3.12`.
  * You can see list by `winget search python`.
  * **Not** msstore version, but winget version.

### Test

```sh
python3 -m testutil discover client

# Launch windows test from WSL
python3 ./client/runaswin.py -m unittest discover client
```
