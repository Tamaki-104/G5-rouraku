"""
モックデータ。E-R図(設計書「5.データ設計」第三正規化)のテーブルを、
そのまま別々の dict リストとして持つ。あえて正規化した形のまま置くことで、
Supabaseへ移しても構造が変わらない。結合は repository 層に任せる。

  物件条件 1─N 住宅情報 ／ 希望条件 1─N 入力情報
  入力情報・住宅情報 1─N 提案管理 ／ 住宅情報 1─N 課題分析 ／ チャットは独立

作成: チーム労楽  /  (c) 2026 チーム労楽
"""

# ── 物件条件（Property condition）────────────────────────────────
PROPERTY_CONDITIONS = [
    {"id": "PC0000001", "area": "渋谷区",   "layout": "1LDK", "station_minutes": 15, "pet_allowed": True},
    {"id": "PC0000002", "area": "池袋区",   "layout": "2LDK", "station_minutes": 20, "pet_allowed": False},
    {"id": "PC0000003", "area": "横浜区",   "layout": "1LDK", "station_minutes": 10, "pet_allowed": False},
    {"id": "PC0000004", "area": "秋葉原区", "layout": "3LDK", "station_minutes": 5,  "pet_allowed": True},
]

# ── 住宅情報（Properties）──────────────────────────────────────
# property_condition_id が 物件条件 への FK。
# building_type=物件の種類（マンション/アパート）。
# deal_type / image_url / description は画面表示用の補完項目（E-R図には無い拡張）。
PROPERTIES = [
    {
        "id": "PRP0000001", "property_condition_id": "PC0000001",
        "name": "ホーム渋谷", "rent": 60000, "building_type": "マンション",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Home+Shibuya",
        "description": "渋谷区の駅徒歩15分のマンション。1LDKで一人暮らし〜カップル向け。ペット相談可。",
    },
    {
        "id": "PRP0000002", "property_condition_id": "PC0000002",
        "name": "サンバ池袋", "rent": 75000, "building_type": "アパート",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Samba+Ikebukuro",
        "description": "池袋エリアの2LDKアパート。やや広めでファミリー向け。ペット不可。",
    },
    {
        "id": "PRP0000003", "property_condition_id": "PC0000003",
        "name": "ホームズ横浜", "rent": 55000, "building_type": "マンション",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Homes+Yokohama",
        "description": "横浜の駅近1LDKマンション。家賃が抑えめでコストパフォーマンス良好。",
    },
    {
        "id": "PRP0000004", "property_condition_id": "PC0000004",
        "name": "3L 秋葉原", "rent": 150000, "building_type": "アパート",
        "deal_type": "購入",
        "image_url": "https://placehold.co/640x400?text=3L+Akihabara",
        "description": "秋葉原の駅徒歩5分・3LDK。広さ重視のファミリー向け物件。購入対象。",
    },
]

# ── 希望条件（Input Condition）─────────────────────────────────
# ユーザーが入力した希望条件。サンプルは設計書 P.18 より。
INPUT_CONDITIONS = [
    {"id": "IC0000001", "area": "新宿区/渋谷区", "layout": "1LDK",       "station_minutes": 20, "pet_allowed": True},
    {"id": "IC0000002", "area": "池袋区",        "layout": "1LDK/2LDK", "station_minutes": 30, "pet_allowed": False},
    {"id": "IC0000003", "area": "秋葉原区",      "layout": "1L以上",     "station_minutes": 5,  "pet_allowed": True},
    {"id": "IC0000004", "area": "横浜区",        "layout": "2LDK以上",   "station_minutes": 10, "pet_allowed": False},
]

# ── 入力情報（Input）──────────────────────────────────────────
# input_condition_id が 希望条件 への FK。
INPUTS = [
    {"id": "INP0000001", "input_condition_id": "IC0000001", "budget": 100000, "created_at": "2026-05-03"},
    {"id": "INP0000002", "input_condition_id": "IC0000002", "budget": 80000,  "created_at": "2026-05-06"},
    {"id": "INP0000003", "input_condition_id": "IC0000003", "budget": 150000, "created_at": "2026-06-02"},
    {"id": "INP0000004", "input_condition_id": "IC0000004", "budget": 70000,  "created_at": "2026-06-05"},
]

# ── 提案管理（Propose）────────────────────────────────────────
PROPOSES = [
    {"id": "PRO0000001", "input_id": "INP0000001", "property_id": "PRP0000001", "score": 70, "rank": "高い", "created_at": "2026-05-03"},
    {"id": "PRO0000002", "input_id": "INP0000002", "property_id": "PRP0000002", "score": 58, "rank": "普通", "created_at": "2026-05-07"},
    {"id": "PRO0000003", "input_id": "INP0000003", "property_id": "PRP0000003", "score": 90, "rank": "高い", "created_at": "2026-06-03"},
    {"id": "PRO0000004", "input_id": "INP0000004", "property_id": "PRP0000004", "score": 65, "rank": "普通", "created_at": "2026-06-05"},
]

# ── 課題分析（Analyze）────────────────────────────────────────
ANALYSES = [
    {"id": "ANL0000001", "property_id": "PRP0000001", "result": "条件に合う項目が多い",                   "created_at": "2026-05-03"},
    {"id": "ANL0000002", "property_id": "PRP0000002", "result": "予算オーバー",                           "created_at": "2026-05-07"},
    {"id": "ANL0000003", "property_id": "PRP0000003", "result": "全ての項目で高いマッチ度",               "created_at": "2026-06-03"},
    {"id": "ANL0000004", "property_id": "PRP0000004", "result": "駅からの距離が少しあるがおおむね希望通り", "created_at": "2026-06-05"},
]

# ── AIチャットボット（Chat）───────────────────────────────────
CHATS = [
    {"id": "CHT0000001", "question": "家賃を少し上げるとより良い物件はありますか", "answer": "同じ条件の物件が3つ見つかりました",            "created_at": "2026-05-05"},
    {"id": "CHT0000002", "question": "条件を変えた方が良い物件はあるでしょうか",   "answer": "条件を変えた方がより良い物件を提案できそうです。", "created_at": "2026-05-07"},
    {"id": "CHT0000003", "question": "この家よりも高いマッチ度の家はありますか",   "answer": "マッチ度の高い物件が見つかりました",              "created_at": "2026-06-04"},
    {"id": "CHT0000004", "question": "条件を変えた方がよろしいでしょうか？",       "answer": "もう少し駅から近い物件に変更しますか？",          "created_at": "2026-06-09"},
]


# ── 入居フロー（賃貸/購入）────────────────────────────────────
# ※ E-R図には無い。物件の取引種別から導出する手続きステップ（設計書「⑤入居までの手順確認」）。
MOVE_IN_FLOWS = {
    "賃貸": [
        {"step": 1, "title": "申込",             "detail": "入居申込書を提出し、物件を仮押さえします。"},
        {"step": 2, "title": "入居審査",         "detail": "収入・保証人などの審査が行われます。"},
        {"step": 3, "title": "契約",             "detail": "重要事項説明を受け、賃貸借契約を締結します。"},
        {"step": 4, "title": "初期費用の支払い", "detail": "敷金・礼金・前家賃などを支払います。"},
        {"step": 5, "title": "引越し",           "detail": "鍵を受け取り、引越し・入居開始です。"},
    ],
    "購入": [
        {"step": 1, "title": "購入申込",          "detail": "買付証明書を提出します。"},
        {"step": 2, "title": "住宅ローン事前審査", "detail": "金融機関でローンの事前審査を受けます。"},
        {"step": 3, "title": "売買契約",          "detail": "重要事項説明後、売買契約を締結し手付金を支払います。"},
        {"step": 4, "title": "ローン本審査・契約", "detail": "住宅ローンの本審査と金銭消費貸借契約を行います。"},
        {"step": 5, "title": "決済・引き渡し",     "detail": "残代金を支払い、物件の引き渡しを受けます。"},
    ],
}
