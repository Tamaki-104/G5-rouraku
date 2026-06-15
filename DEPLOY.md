# デプロイ手順（Supabase + GitHub + Vercel）

## 全体の流れ
1. Supabase にテーブル作成＋サンプルデータ投入
2. ローカルで本接続テスト（USE_MOCK=false）
3. GitHub に push
4. Vercel に GitHub 連携でデプロイ＆環境変数設定

---

## 1. Supabase 準備
1. Supabase ダッシュボード → 対象プロジェクト → **SQL Editor**
2. [`data/schema.sql`](data/schema.sql) の中身を貼り付けて実行（テーブル作成）
3. 続けて [`data/seed.sql`](data/seed.sql) を貼り付けて実行（サンプルデータ投入）
4. **Project Settings → API** から以下を控える
   - `Project URL` → `SUPABASE_URL`
   - `anon public` キー → `SUPABASE_ANON_KEY`

> 注: 現在は読み取り中心のため anon キーで動作します。RLS（行レベルセキュリティ）を有効にする場合は
> properties / property_conditions などに SELECT 許可ポリシーを追加してください。

## 2. ローカルで本接続テスト
```powershell
# .env を作成
copy .env.example .env
# .env を編集し USE_MOCK=false と SUPABASE_URL / SUPABASE_ANON_KEY を設定

python -m pip install -r requirements.txt
python app.py
```
http://127.0.0.1:5000 を開き、物件提案にSupabaseのデータが出れば成功。

## 3. GitHub へ push
```powershell
git init
git add .
git commit -m "宅ラーク 不動産マッチングシステム 初期実装"
git branch -M main
git remote add origin https://github.com/<ユーザー名>/<リポジトリ名>.git
git push -u origin main
```
> `.env` は `.gitignore` 済みなので push されません（キーは漏れません）。

## 4. Vercel デプロイ
1. Vercel → **Add New → Project** → 対象の GitHub リポジトリを Import
2. Framework Preset は **Other**（`vercel.json` の設定で Python として動きます）
3. **Settings → Environment Variables** に以下を登録
   | Key | Value |
   |---|---|
   | `USE_MOCK` | `false` |
   | `FLASK_SECRET_KEY` | 任意のランダム文字列 |
   | `SUPABASE_URL` | Supabase の Project URL |
   | `SUPABASE_ANON_KEY` | anon public キー |
   | `GEMINI_API_KEY` | （任意）Gemini APIキー |
4. **Deploy** を実行。以降は GitHub に push するたび自動デプロイされます。

## 補足
- Vercel は `vercel.json` の `@vercel/python` ビルドで `app.py` の Flask `app` をサーバーレス関数として実行します。
- Flask セッションは署名付きクッキー方式のため、サーバーレスでも状態を保持できます（`FLASK_SECRET_KEY` を必ず固定値で設定）。
