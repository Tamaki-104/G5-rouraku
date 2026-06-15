# 宅ラーク — 不動産マッチングシステム（試作版）

チーム「労楽」内部設計書をもとにした、AI不動産マッチングWebアプリのPython実装です。

## 機能
1. **条件入力** — 希望エリア・予算・間取り・駅距離・ペット可否を入力（必須/値チェックあり）
2. **物件提案** — AIマッチングエンジンが適合度（%）を計算し、高い順に提案。合致物件がなければ条件緩和候補を提示
3. **物件詳細・課題分析** — 物件詳細を表示し、AIが希望との乖離点・懸念点を分析
4. **AIコンシェルジュ** — チャットで質問。物件と無関係な質問は対象外案内
5. **入居までの手順** — 物件種別（賃貸/購入）ごとの手続きフローを表示

## 技術構成
- Python / Flask（画面 + API を単一プロセスで提供）
- フロント：Jinja2 テンプレート + バニラJS
- データ：現在は**モックデータ**（`data/mock_data.py`）。**E-R図（第三正規化）に準拠**し、物件条件/住宅情報/希望条件/入力情報/提案管理/課題分析/チャットの7テーブルを正規化して保持。リポジトリ層が結合して画面へ渡す。
- DBスキーマ：`data/schema.sql`（PostgreSQL/Supabase用DDL。E-R図と1対1対応）
- AI：現在は**モックAI**（ルールベース、`services/ai.py`）

> 設計書本体は Next.js/Vercel/Supabase/Gemini 前提ですが、本実装はご指定により Python で作成しています。
> `USE_MOCK=false` ＋ APIキー設定で Gemini / Supabase への本接続に切り替えられる構造です（`services/ai.py` / `services/repository.py` の TODO 部分を実装）。

## 動作環境
- Windows 10 以降（Python 3.10+）

## セットアップ & 起動
```powershell
# 依存パッケージのインストール
python -m pip install -r requirements.txt

# 起動
python app.py
```
ブラウザで http://127.0.0.1:5000 を開く。

## 本接続（任意・今後）
1. `.env.example` を `.env` にコピー
2. `USE_MOCK=false`、`GEMINI_API_KEY` / `SUPABASE_URL` / `SUPABASE_ANON_KEY` を設定
3. `services/repository.py`（Supabase）と `services/ai.py`（Gemini）の TODO を実装

## ディレクトリ構成
```
app.py                  Flask 本体（ルーティング）
config.py               設定（.env 読み込み・USE_MOCKフラグ）
data/mock_data.py       モックデータ（E-R図準拠の正規化テーブル群）
data/schema.sql         DB スキーマ DDL（Supabase/PostgreSQL用・E-R図対応）
data/seed.sql           サンプルデータ投入用 SQL
vercel.json             Vercel デプロイ設定（@vercel/python）
DEPLOY.md               Supabase + GitHub + Vercel デプロイ手順
services/
  repository.py         データアクセス層（モック↔Supabase切替）
  matching.py           AIマッチングエンジン（適合度計算）
  ai.py                 AI（課題分析・チャット。モック↔Gemini切替）
templates/              画面（Jinja2）
static/                 CSS / JS
```
