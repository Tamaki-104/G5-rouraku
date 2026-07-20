-- ============================================================
-- 宅ラーク 不動産マッチングシステム — データベーススキーマ
-- E-R図（第三正規化）に準拠 / PostgreSQL（Supabase）用 DDL
-- USE_MOCK=false での本接続時に、このスクリプトでテーブルを作成する。
-- ============================================================

-- ── 物件条件（Property condition）──────────────────────────
CREATE TABLE IF NOT EXISTS property_conditions (
    id              TEXT PRIMARY KEY,          -- 物件条件ID (例: PC0000001)
    prefecture      TEXT NOT NULL DEFAULT '',  -- 都道府県（県外判定に使用）
    area            TEXT NOT NULL,             -- エリア（地区）
    layout          TEXT NOT NULL,             -- 間取り
    station_minutes INTEGER NOT NULL,          -- 駅からの距離（分）
    pet_allowed     BOOLEAN NOT NULL DEFAULT FALSE  -- ペット許可
);

-- ── 住宅情報（Properties）─────────────────────────────────
CREATE TABLE IF NOT EXISTS properties (
    id                   TEXT PRIMARY KEY,     -- 物件ID (例: PRP0000001)
    property_condition_id TEXT NOT NULL REFERENCES property_conditions(id),  -- FK→物件条件
    name                 TEXT NOT NULL,        -- 物件名
    rent                 INTEGER NOT NULL,     -- 家賃
    building_type        TEXT NOT NULL,        -- 物件の種類（マンション/アパート）
    -- 以下は画面表示用の拡張（E-R図には無い）
    deal_type            TEXT NOT NULL DEFAULT '賃貸',  -- 取引種別（賃貸/購入）
    image_url            TEXT,
    description          TEXT
);

-- ── 希望条件（Input Condition）────────────────────────────
CREATE TABLE IF NOT EXISTS input_conditions (
    id              TEXT PRIMARY KEY,          -- 希望条件ID (例: IC0000001)
    prefecture      TEXT NOT NULL DEFAULT '',  -- 希望都道府県
    area            TEXT NOT NULL,             -- 希望エリア（地区）
    layout          TEXT NOT NULL,             -- 希望の間取り
    station_minutes INTEGER,                   -- 駅からの距離
    pet_allowed     BOOLEAN NOT NULL DEFAULT FALSE  -- ペット許可
);

-- ── 入力情報（Input）─────────────────────────────────────
CREATE TABLE IF NOT EXISTS inputs (
    id                 TEXT PRIMARY KEY,        -- 入力ID (例: INP0000001)
    input_condition_id TEXT NOT NULL REFERENCES input_conditions(id),  -- FK→希望条件
    budget             INTEGER NOT NULL,        -- 予算上限
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- 作成日時
);

-- ── 提案管理（Propose）───────────────────────────────────
CREATE TABLE IF NOT EXISTS proposes (
    id          TEXT PRIMARY KEY,               -- 提案ID (例: PRO0000001)
    input_id    TEXT NOT NULL REFERENCES inputs(id),      -- FK1→入力情報
    property_id TEXT NOT NULL REFERENCES properties(id),  -- FK2→住宅情報
    score       INTEGER NOT NULL,               -- 適正値（適合度%）
    rank        TEXT,                           -- 順位付け（高い/普通/低い）
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- 提案日時
);

-- ── 課題分析（Analyze）───────────────────────────────────
CREATE TABLE IF NOT EXISTS analyses (
    id          TEXT PRIMARY KEY,               -- 分析ID (例: ANL0000001)
    property_id TEXT NOT NULL REFERENCES properties(id),  -- FK→住宅情報
    result      TEXT NOT NULL,                  -- 分析結果
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- 分析日時
);

-- ── AIチャットボット（Chat）──────────────────────────────
-- アプリは question / answer のみINSERTするため、id は自動採番（CHT0000001形式）。
CREATE SEQUENCE IF NOT EXISTS chats_seq START 1;
CREATE TABLE IF NOT EXISTS chats (
    id         TEXT PRIMARY KEY
                 DEFAULT ('CHT' || lpad(nextval('chats_seq')::text, 7, '0')),  -- チャットID
    question   TEXT NOT NULL,                   -- 質問内容
    answer     TEXT NOT NULL,                   -- 回答内容
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- 送信日時
);

-- 検索を高速化するインデックス（任意）
CREATE INDEX IF NOT EXISTS idx_properties_condition ON properties(property_condition_id);
CREATE INDEX IF NOT EXISTS idx_proposes_input       ON proposes(input_id);
CREATE INDEX IF NOT EXISTS idx_proposes_property    ON proposes(property_id);
CREATE INDEX IF NOT EXISTS idx_analyses_property    ON analyses(property_id);
