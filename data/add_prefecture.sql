-- ============================================================
-- 既存の Supabase DB へ都道府県列を追加する移行SQL
-- （SQL Editor で1回実行する。新規構築なら schema.sql に含まれるため不要）
--
-- 目的: 県外判定（希望と異なる都道府県の物件を適合率0%で除外）を、
--       ハードコード対応表ではなく物件データ内蔵の値で行えるようにする。
-- ============================================================

ALTER TABLE property_conditions
    ADD COLUMN IF NOT EXISTS prefecture TEXT NOT NULL DEFAULT '';

-- 既存データへ都道府県を設定
UPDATE property_conditions SET prefecture = '東京都'
 WHERE area IN ('渋谷区','新宿区','池袋区','秋葉原区','中野区','台東区','文京区','足立区','港区');
UPDATE property_conditions SET prefecture = '神奈川県'
 WHERE area IN ('横浜区');

-- 確認用: 全行に prefecture が入っていること
-- SELECT id, prefecture, area FROM property_conditions ORDER BY id;
