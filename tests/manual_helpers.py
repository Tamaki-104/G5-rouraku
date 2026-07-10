"""
手動テスト用の入力ヘルパー。ドライバの「手動モード」で、テスターが引数を対話入力する。

いずれも空Enterで既定値を採用する。バグを持ち込まないよう単純に保つ（授業資料10.6）。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""


def ask_str(label, default):
    """文字列を入力させる。空Enterなら default。"""
    s = input(f"    {label} [{default}]: ").strip()
    return s if s else default


def ask_int(label, default):
    """整数を入力させる。空Enterなら default。数値以外は再入力。"""
    while True:
        s = input(f"    {label} [{default}]: ").strip()
        if not s:
            return default
        try:
            return int(s)
        except ValueError:
            print("      数値を入力してください。")


def ask_bool(label, default):
    """y/n を入力させる。空Enterなら default。"""
    d = "y" if default else "n"
    s = input(f"    {label} (y/n) [{d}]: ").strip().lower()
    if not s:
        return default
    return s.startswith("y")


def ask_choice(label, options, default):
    """選択肢から1つ選ばせる。options は (キー, 説明) のリスト。空Enterなら default。"""
    print(f"    {label}")
    for key, desc in options:
        print(f"      {key}) {desc}")
    keys = [key for key, _ in options]
    while True:
        s = input(f"    選択 [{default}]: ").strip()
        if not s:
            return default
        if s in keys:
            return s
        print(f"      {'/'.join(keys)} から選んでください。")
