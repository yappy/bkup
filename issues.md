# リポジトリレビュー

対象コミットは `9abfe95` です。最優先は、`clean` と `cloudclean` がバックアップと無関係なファイルまで削除する問題です。

## P1

1. **`clean` と `cloudclean` がアーカイブ以外のファイルを削除する。** `name_parse_str()` は未対応の拡張子に `False` を返しますが、呼び出し側は `is not None` で判定するため、`notes.txt` や `backup.log` も削除候補に入ります。両コマンドで `--keep-count 0` を指定し、`notes.txt` が削除されることを確認しました。 [src/commands/util.py:44](src/commands/util.py#L44)
2. **自動バックアップが失敗後も削除処理へ進み、終了コード `0` を返す。** WSL・Windows 向けスクリプトは各処理の出力を `tee` に流し、Python 側の失敗を検知せずに続行します。WSL 向けスクリプトに存在しないコピー元を渡したところ、`archive` の失敗後に `clean` が実行され、終了コードは `0` でした。 [scripts/main_wsl.sh:32](scripts/main_wsl.sh#L32) · [scripts/main_win.sh:33](scripts/main_win.sh#L33)

## P2

3. **`archive --dry-run` が `latest.txt` を上書きする。** プレビューでも、`latest.txt` に作成予定のアーカイブのパスが記録されます。正常なバックアップの直後に別タグでプレビューすると、後続の `upload` が存在しないファイルを参照して失敗することを確認しました。 [src/commands/archive.py:118](src/commands/archive.py#L118)
4. **`sync` が Robocopy の失敗を呼び出し元に伝えない。** Robocopy が失敗を示す終了コード `8` 以上を返しても、警告だけを出し、`sync` は最後に `OK` を記録します。自動実行では、不完全な同期先をそのままアーカイブする可能性があります。コード上で確認しました。 [src/commands/sync.py:68](src/commands/sync.py#L68)
5. **`cloudsetup` が rclone の未インストール時やマイナー更新時に機能しない。** 実行ファイルがない場合の `FileNotFoundError` が伝播し、ダウンロード処理まで到達しません。また、バージョン比較が文字列の2文字目を参照するため、`v1.69.0` と `v1.70.0` を同じバージョンと判定します。 [src/commands/cloudsetup.py:11](src/commands/cloudsetup.py#L11) · [src/commands/cloudsetup.py:43](src/commands/cloudsetup.py#L43)

## 検証範囲

Linux で `./test.sh` の既存5件と `./shellcheck.sh` は通過しました。`cloudclean` の再現には rclone のローカルバックエンドを使用しました。Windows／Robocopy と実クラウドでの動作は未検証です。
