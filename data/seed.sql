-- ============================================================
-- サンプルデータ投入（schema.sql 実行後に流す）
-- E-R図 / 設計書のサンプル物件に準拠。
-- ============================================================

-- 物件条件
INSERT INTO property_conditions (id, prefecture, area, layout, station_minutes, pet_allowed) VALUES
  ('PC0000001', '東京都',   '渋谷区',   '1LDK', 15, TRUE),
  ('PC0000002', '東京都',   '池袋区',   '2LDK', 20, FALSE),
  ('PC0000003', '神奈川県', '横浜区',   '1LDK', 10, FALSE),
  ('PC0000004', '東京都',   '秋葉原区', '3LDK', 5,  TRUE)
ON CONFLICT (id) DO NOTHING;

-- 住宅情報
INSERT INTO properties (id, property_condition_id, name, rent, building_type, deal_type, image_url, description) VALUES
  ('PRP0000001', 'PC0000001', 'ホーム渋谷',   60000,  'マンション', '賃貸', 'https://placehold.co/640x400?text=Home+Shibuya',    '渋谷区の駅徒歩15分のマンション。1LDKで一人暮らし〜カップル向け。ペット相談可。'),
  ('PRP0000002', 'PC0000002', 'サンバ池袋',   75000,  'アパート',   '賃貸', 'https://placehold.co/640x400?text=Samba+Ikebukuro', '池袋エリアの2LDKアパート。やや広めでファミリー向け。ペット不可。'),
  ('PRP0000003', 'PC0000003', 'ホームズ横浜', 55000,  'マンション', '賃貸', 'https://placehold.co/640x400?text=Homes+Yokohama',  '横浜の駅近1LDKマンション。家賃が抑えめでコストパフォーマンス良好。'),
  ('PRP0000004', 'PC0000004', '3L 秋葉原',    150000, 'アパート',   '購入', 'https://placehold.co/640x400?text=3L+Akihabara',    '秋葉原の駅徒歩5分・3LDK。広さ重視のファミリー向け物件。購入対象。')
ON CONFLICT (id) DO NOTHING;

-- 希望条件
INSERT INTO input_conditions (id, area, layout, station_minutes, pet_allowed) VALUES
  ('IC0000001', '新宿区/渋谷区', '1LDK',     20, TRUE),
  ('IC0000002', '池袋区',        '1LDK/2LDK',30, FALSE),
  ('IC0000003', '秋葉原区',      '1L以上',   5,  TRUE),
  ('IC0000004', '横浜区',        '2LDK以上', 10, FALSE)
ON CONFLICT (id) DO NOTHING;

-- 入力情報
INSERT INTO inputs (id, input_condition_id, budget, created_at) VALUES
  ('INP0000001', 'IC0000001', 100000, '2026-05-03'),
  ('INP0000002', 'IC0000002', 80000,  '2026-05-06'),
  ('INP0000003', 'IC0000003', 150000, '2026-06-02'),
  ('INP0000004', 'IC0000004', 70000,  '2026-06-05')
ON CONFLICT (id) DO NOTHING;

-- 提案管理
INSERT INTO proposes (id, input_id, property_id, score, rank, created_at) VALUES
  ('PRO0000001', 'INP0000001', 'PRP0000001', 70, '高い', '2026-05-03'),
  ('PRO0000002', 'INP0000002', 'PRP0000002', 58, '普通', '2026-05-07'),
  ('PRO0000003', 'INP0000003', 'PRP0000003', 90, '高い', '2026-06-03'),
  ('PRO0000004', 'INP0000004', 'PRP0000004', 65, '普通', '2026-06-05')
ON CONFLICT (id) DO NOTHING;

-- 課題分析
INSERT INTO analyses (id, property_id, result, created_at) VALUES
  ('ANL0000001', 'PRP0000001', '条件に合う項目が多い',                   '2026-05-03'),
  ('ANL0000002', 'PRP0000002', '予算オーバー',                           '2026-05-07'),
  ('ANL0000003', 'PRP0000003', '全ての項目で高いマッチ度',               '2026-06-03'),
  ('ANL0000004', 'PRP0000004', '駅からの距離が少しあるがおおむね希望通り', '2026-06-05')
ON CONFLICT (id) DO NOTHING;
