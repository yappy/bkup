# リポジトリレビュー

レビュー対象コミットは `9abfe95` です。P1 は2件とも修正済みで、未対応は P2 の4番です。

## P1

1. **［修正済み］`clean` と `cloudclean` がアーカイブ以外のファイルを削除する。** `name_parse_str()` は未対応の拡張子に `False` を返しますが、呼び出し側は `is not None` で判定するため、`notes.txt` や `backup.log` も削除候補に入ります。両コマンドで `--keep-count 0` を指定し、`notes.txt` が削除されることを確認しました。 [src/commands/util.py:44](src/commands/util.py#L44)

   拡張子がない場合と未対応の拡張子の場合に `None` を返すよう修正しました。回帰テストを含む全6件が通過し、`cloudclean` でも rclone のローカルバックエンドで対象のアーカイブだけが削除されることを確認しました。 [src/tests/test_client.py:149](src/tests/test_client.py#L149)

2. **［修正済み］自動バックアップが失敗後も削除処理へ進み、終了コード `0` を返す。** WSL・Windows 向けスクリプトは各処理の出力を `tee` に流し、Python 側の失敗を検知せずに続行していました。WSL 向けスクリプトに存在しないコピー元を渡したところ、`archive` の失敗後に `clean` が実行され、終了コードは `0` でした。

   両スクリプトで `pipefail` を有効にし、バックアップ処理のパイプラインが失敗した時点で終了ステータスを呼び出し元に返すよう修正しました。Linux で各工程に失敗を注入し、ログにエラーを記録して後続処理を中止することを確認しました。存在しないコピー元を指定した実行でも、両スクリプトが終了コード `1` を返し、既存のアーカイブを保持しました。 [scripts/main_wsl.sh:10](scripts/main_wsl.sh#L10) · [scripts/main_win.sh:10](scripts/main_win.sh#L10)

## P2

3. **［修正済み］`archive --dry-run` が `latest.txt` を上書きする。** プレビューでも、`latest.txt` に作成予定のアーカイブのパスが記録されます。正常なバックアップの直後に別タグでプレビューすると、後続の `upload` が存在しないファイルを参照して失敗することを確認しました。

   `latest.txt` への書き込みを通常実行時に限定しました。プレビューで `latest.txt` が新規作成も上書きもされないことを回帰テストで確認しました。Linux では、通常実行の後に別タグでプレビューしても、`upload` が元のアーカイブをローカルの転送先へコピーできました。 [src/commands/archive.py:118](src/commands/archive.py#L118) · [src/tests/test_client.py:239](src/tests/test_client.py#L239)

4. **`sync` が Robocopy の失敗を呼び出し元に伝えない。** Robocopy が失敗を示す終了コード `8` 以上を返しても、警告だけを出し、`sync` は最後に `OK` を記録します。自動実行では、不完全な同期先をそのままアーカイブする可能性があります。コード上で確認しました。 [src/commands/sync.py:68](src/commands/sync.py#L68)
5. **［修正済み］`cloudsetup` が rclone の未インストール時やマイナー更新時に機能しない。** 実行ファイルがない場合の `FileNotFoundError` が伝播し、ダウンロード処理まで到達しません。また、バージョン比較が文字列の2文字目を参照するため、`v1.69.0` と `v1.70.0` を同じバージョンと判定します。

   実行ファイルが見つからない場合は未インストールとして扱い、バージョンの各要素を数値で比較するよう修正しました。Linux で `rclone` と `wget` の代替コマンドを使い、未インストール時と更新が必要な場合にダウンロードへ進むこと、同じか新しいバージョンではダウンロードを省くこと、ダウンロードに失敗した場合に一時ディレクトリを削除することを確認しました。 [src/commands/cloudsetup.py:12](src/commands/cloudsetup.py#L12) · [src/tests/test_client.py:98](src/tests/test_client.py#L98)

## 検証範囲

Linux で `./test.sh` の既存5件と `./shellcheck.sh` は通過しました。`cloudclean` の再現には rclone のローカルバックエンドを使用しました。Windows／Robocopy と実クラウドでの動作は未検証です。
