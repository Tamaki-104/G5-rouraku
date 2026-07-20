"""
モックデータ。E-R図(設計書「5.データ設計」第三正規化)のテーブルを、
そのまま別々の dict リストとして持つ。あえて正規化した形のまま置くことで、
Supabaseへ移しても構造が変わらない。結合は repository 層に任せる。

  物件条件 1─N 住宅情報 ／ 希望条件 1─N 入力情報
  入力情報・住宅情報 1─N 提案管理 ／ 住宅情報 1─N 課題分析 ／ チャットは独立

作成: チーム労楽  /  (c) 2026 チーム労楽
"""

# ── 物件条件（Property condition）────────────────────────────────
# prefecture=都道府県。県外判定は物件データに内蔵したこの値と、
# 検索フォームで入力された希望都道府県を直接比較して行う。
PROPERTY_CONDITIONS = [
    {"id": "PC0000001", "prefecture": "東京都",   "area": "渋谷区",   "layout": "1LDK", "station_minutes": 15, "pet_allowed": True},
    {"id": "PC0000002", "prefecture": "東京都",   "area": "池袋区",   "layout": "2LDK", "station_minutes": 20, "pet_allowed": False},
    {"id": "PC0000003", "prefecture": "神奈川県", "area": "横浜区",   "layout": "1LDK", "station_minutes": 10, "pet_allowed": False},
    {"id": "PC0000004", "prefecture": "東京都",   "area": "秋葉原区", "layout": "3LDK", "station_minutes": 5,  "pet_allowed": True},
    {"id": "PC0000005", "prefecture": "東京都",   "area": "中野区",   "layout": "1DK",  "station_minutes": 40, "pet_allowed": False},
    {"id": "PC0000006", "prefecture": "東京都",   "area": "台東区",   "layout": "1LDK", "station_minutes": 20, "pet_allowed": True},
    {"id": "PC0000007", "prefecture": "東京都",   "area": "文京区",   "layout": "1LDK", "station_minutes": 5,  "pet_allowed": False},
    {"id": "PC0000008", "prefecture": "東京都",   "area": "足立区",   "layout": "2LDK", "station_minutes": 30, "pet_allowed": False},
    {"id": "PC0000009", "prefecture": "東京都",   "area": "港区",     "layout": "2LDK", "station_minutes": 5,  "pet_allowed": True},
    # 以下5件はSUUMO家賃相場（2026年4月時点、区内平均）を参考に追加。
    # 実在の個別物件ではなく、区ごとの相場を反映した想定データ。
    {"id": "PC0000010", "prefecture": "東京都",   "area": "新宿区",   "layout": "1LDK", "station_minutes": 8,  "pet_allowed": True},
    {"id": "PC0000011", "prefecture": "東京都",   "area": "目黒区",   "layout": "2LDK", "station_minutes": 12, "pet_allowed": False},
    {"id": "PC0000012", "prefecture": "東京都",   "area": "品川区",   "layout": "1LDK", "station_minutes": 10, "pet_allowed": True},
    {"id": "PC0000013", "prefecture": "東京都",   "area": "世田谷区", "layout": "1LDK", "station_minutes": 15, "pet_allowed": False},
    {"id": "PC0000014", "prefecture": "東京都",   "area": "杉並区",   "layout": "1DK",  "station_minutes": 9,  "pet_allowed": False},
]

# エリア名 -> 都道府県の補完表。
# Supabase側にまだ prefecture 列が無い行を読んだ場合のフォールバック専用。
# （物件データに prefecture を内蔵済みなら参照されない）
AREA_PREFECTURES = {
    "渋谷区": "東京都", "新宿区": "東京都", "池袋区": "東京都", "秋葉原区": "東京都",
    "中野区": "東京都", "台東区": "東京都", "文京区": "東京都", "足立区": "東京都",
    "港区": "東京都", "横浜区": "神奈川県",
    "目黒区": "東京都", "品川区": "東京都", "世田谷区": "東京都", "杉並区": "東京都",
}

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
    {
        "id": "PRP0000005", "property_condition_id": "PC0000005",
        "name": "弟切荘", "rent": 45000, "building_type": "アパート",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Otogiri_So",
        "description": "中野区の1DKアパート。破格の家賃。",
    },
    {
        "id": "PRP0000006", "property_condition_id": "PC0000006",
        "name": "サニーコート台東", "rent": 65000, "building_type": "アパート",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Sunny_Coat_Taito",
        "description": "台東区の1LDKアパート。周辺にコンビニやスーパーあり、ペット可。",
    },
    {
        "id": "PRP0000007", "property_condition_id": "PC0000007",
        "name": "アネモネ文京", "rent": 70000, "building_type": "マンション",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Anemone_Bunkyo",
        "description": "文京区の1LDKマンション。駅近で、冬場の通学通勤も快適。",
    },
    {
        "id": "PRP0000008", "property_condition_id": "PC0000008",
        "name": "プラザ足立北綾瀬", "rent": 100000, "building_type": "マンション",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Plaza_Adachi_Kita-ayase",
        "description": "足立区の2LDKマンション。落ち着いた住宅街にある築浅物件。",
    },
    {
        "id": "PRP0000009", "property_condition_id": "PC0000009",
        "name": "メゾン・ド・ポート", "rent": 200000, "building_type": "アパート",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Maison_de_Port",
        "description": "港区の2LDKアパート。最寄り駅から徒歩5分で、日当たりも良好。ペット可。",
    },
    # 以下5件のrentはSUUMO家賃相場（各区の1LDK/2LDK等・平均、2026年4月時点）を
    # 参考値として使用。name/description/image_urlは他の行と同様、表示用の仮データ。
    {
        "id": "PRP0000010", "property_condition_id": "PC0000010",
        "name": "コンフォート新宿", "rent": 171000, "building_type": "マンション",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Comfort_Shinjuku",
        "description": "新宿区の駅徒歩8分・1LDKマンション。繁華街へのアクセスが良く、ペット相談可。",
    },
    {
        "id": "PRP0000011", "property_condition_id": "PC0000011",
        "name": "グランドヒルズ目黒", "rent": 260000, "building_type": "マンション",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Grand_Hills_Meguro",
        "description": "目黒区の2LDKマンション。落ち着いた住宅街で、ファミリー層にも人気のエリア。ペット不可。",
    },
    {
        "id": "PRP0000012", "property_condition_id": "PC0000012",
        "name": "サニーテラス品川", "rent": 129000, "building_type": "アパート",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Sunny_Terrace_Shinagawa",
        "description": "品川区の駅徒歩10分・1LDKアパート。都心へのアクセスが良く、ペット相談可。",
    },
    {
        "id": "PRP0000013", "property_condition_id": "PC0000013",
        "name": "グリーンコート世田谷", "rent": 143000, "building_type": "マンション",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Green_Court_Setagaya",
        "description": "世田谷区の1LDKマンション。緑が多く落ち着いた住環境。ペット不可。",
    },
    {
        "id": "PRP0000014", "property_condition_id": "PC0000014",
        "name": "陽だまり荘杉並", "rent": 69000, "building_type": "アパート",
        "deal_type": "賃貸",
        "image_url": "https://placehold.co/640x400?text=Hidamari_So_Suginami",
        "description": "杉並区の1DKアパート。家賃を抑えたい一人暮らし向け。ペット不可。",
    },
]

# ── 希望条件（Input Condition）─────────────────────────────────
# prefecture=希望都道府県。検索フォームの入力に対応する。
INPUT_CONDITIONS = [
    {"id": "IC0000001", "prefecture": "東京都",   "area": "新宿区/渋谷区", "layout": "1LDK",           "station_minutes": 20, "pet_allowed": True},
    {"id": "IC0000002", "prefecture": "東京都",   "area": "池袋区",        "layout": "1LDK/2LDK",      "station_minutes": 30, "pet_allowed": False},
    {"id": "IC0000003", "prefecture": "東京都",   "area": "秋葉原区",      "layout": "1L以上",         "station_minutes": 5,  "pet_allowed": True},
    {"id": "IC0000004", "prefecture": "神奈川県", "area": "横浜区",        "layout": "2LDK以上",       "station_minutes": 10, "pet_allowed": False},
    {"id": "IC0000005", "prefecture": "東京都",   "area": "中野区",        "layout": "1DK/1LDK",       "station_minutes": 40, "pet_allowed": False},
    {"id": "IC0000006", "prefecture": "東京都",   "area": "台東区",        "layout": "1LDK/2LDK",      "station_minutes": 20, "pet_allowed": True},
    {"id": "IC0000007", "prefecture": "東京都",   "area": "文京区",        "layout": "1LDK以上",       "station_minutes": 5,  "pet_allowed": False},
    {"id": "IC0000008", "prefecture": "東京都",   "area": "足立区",        "layout": "2LDK/2LDK以上",  "station_minutes": 30, "pet_allowed": False},
    {"id": "IC0000009", "prefecture": "東京都",   "area": "港区",          "layout": "2LDK/2LDK以上",  "station_minutes": 5,  "pet_allowed": True},
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
    {"id": "PRO0000003", "input_id": "INP0000003", "property_id": "PRP0000004", "score": 90, "rank": "高い", "created_at": "2026-06-03"},
    {"id": "PRO0000004", "input_id": "INP0000004", "property_id": "PRP0000003", "score": 65, "rank": "普通", "created_at": "2026-06-05"},
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
