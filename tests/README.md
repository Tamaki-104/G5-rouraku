# 単体テスト（ドライバ・スタブ）

ソフトウェア設計実践論 第10章に基づく単体テスト（ホワイトボックステスト）用の
ドライバとスタブ。授業資料に準拠し、実行すると「呼び出し・引数・期待値・戻り値」を
表示するので、目視で合否を判定する。バグは GitHub Issues にチケット登録する。

## 構成

| ファイル | 役割 |
|---|---|
| `driver_matching.py` | matching.py のドライバ（純ロジック・スタブ不要／18項目） |
| `driver_ai.py` | ai.py のドライバ（＋Geminiスタブ／10項目） |
| `driver_repository.py` | repository.py のドライバ（＋Supabaseスタブ／6項目） |
| `driver_favorites.py` | favorites.py のドライバ（test_client＋repositoryスタブ／6項目） |
| `stub_gemini.py` | Geminiスタブ（外部AI呼び出しの代役） |
| `stub_supabase.py` | Supabaseスタブ（外部DB呼び出しの代役） |
| `stub_repository.py` | repositoryスタブ（データ層の代役） |

## ドライバとスタブの考え方（授業資料10.6）

- **ドライバ**：テスト対象の関数を起動する。引数（正常・異常）をセットして呼び出し、
  戻り値を表示する。単体テストでは必ず作成する。
- **スタブ**：テスト対象が依存する外部モジュールの「振り」をする。呼び出されたことと
  引数を表示し、あらかじめ用意した戻り値を返す（モードで正常・異常・例外を切替）。
  これにより、外部（Gemini・Supabase）が無くても、また外部の不具合に影響されずに、
  対象モジュール単体の分岐を検証できる。

宅ラークでスタブが必要なのは外部依存を持つ ai.py（Gemini）・repository.py（Supabase）、
およびそれらに依存する favorites.py。matching.py は純ロジックのためドライバのみ。

## 実行方法

プロジェクト直下（`app.py` のある場所）で、Windows は次のように実行する。

```powershell
python tests/driver_matching.py
python tests/driver_ai.py
python tests/driver_repository.py
python tests/driver_favorites.py
```

各項目の「期待」と「戻り値」を照らし、一致すれば合格。1つでも不一致があれば、
ソース修正後に全項目を再テストする。

## テスト観点（ホワイトボックス）

各ドライバは、対象関数の分岐を真偽両方・境界値まで通すよう項目を並べている。

- **matching**：区切り分解、エリア/間取り一致、県外判定の4分岐、適合度（全一致・各項目
  ミス・ペット不問・県外0%）、順位ラベルの境界（70・40）、降順ソート、元データ非破壊
- **ai**：モック経路 / 実AI経路（スタブ）/ API例外時のフォールバック、モック応答の
  話題分岐、文末整形（句点あり・なし）
- **repository**：モック経路 / Supabase正常取得 / 取得0件 / 取得失敗フォールバック
- **favorites**：property_id 未指定→400、追加、解除、空一覧、一覧表示、存在しないIDの除外

## バグ管理（GitHub Issues）

不合格項目が出たら、GitHub Issues にチケットを作成する。
- ラベル/トラッカーを「バグ」、ステータスは新規
- 再現手順（どのドライバのどの項目か）、期待値、実際の戻り値を記載
- 担当者を割り当て → 進行中 → 解決（確認待ち）→ 終了、と遷移させる
