-- ============================================================
-- Supabase 初期設定（schema.sql 実行後に SQL Editor で1回実行）
-- デモ用途: RLS を無効化し、publishable(anon) キーで読み書き可能にする。
--
-- ※ 本番運用では RLS を有効のまま、適切なポリシーを設定すること。
--   例（読み取りのみ公開・chatsは投稿可）:
--     alter table properties enable row level security;
--     create policy "public_read" on properties for select using (true);
--     create policy "public_insert" on chats for insert with check (true);
-- ============================================================

alter table property_conditions disable row level security;
alter table properties          disable row level security;
alter table input_conditions    disable row level security;
alter table inputs              disable row level security;
alter table proposes            disable row level security;
alter table analyses            disable row level security;
alter table chats               disable row level security;

-- サンプルデータは repository 側から REST 経由で投入するため、
-- ここでの seed 実行は任意（data/seed.sql を使ってもよい）。
