import pyxel

font = pyxel.Font("k8x12.bdf")

pyxel.init(255, 200, title="HappyBirthDay!", fps=30)

# 🎵 BGM（Happy Birthday to You）
pyxel.sounds[1].set(
    "C4 C4 D4 C4 C4 F4 E4 E4 R "
    "C4 C4 D4 C4 C4 G4 F4 F4 R "
    "C4 C4 A4 A4 F4 E4 D4 D4 D4 R R "
    "A4 A4 F4 F4 G4 G4 F4 F4 F4 R R R ",
    "T", "5", "N", 60
)
pyxel.musics[0].set([1])

# 🔑 効果音：鍵が開く音
pyxel.sounds[2].set("C3 G3 C4 R", "T", "3", "N", 8)

# 🎵 room1用BGM
pyxel.sounds[0].set(
    "C4 E4 G4 B4 G4 E4 C4 D4 F4 A4 F4 D4 C4 "
    "E4 G4 C4 A4 F4 D4 B3 C4 E4 G4 E4 D4 C4",
    "T", "1", "F", 50
)
pyxel.play(0, 0, loop=True)

# 画像読み込み
pyxel.images[0].load(0, 0, "assets/room.png", True)
pyxel.images[2].load(0, 0, "assets/window.png")
pyxel.images[1].load(0, 0, "assets/chara_top.png")
pyxel.images[1].load(32, 0, "assets/chara_left.png")
pyxel.images[1].load(64, 0, "assets/chara_right.png")
pyxel.images[1].load(96, 0, "assets/chara_back.png")
pyxel.images[2].load(0, 35, "assets/letter.png")  # 📩 手紙画像を別座標に読み込み

player_x, player_y = 208, 112
player_dir = "front"
player_size = 32

show_message = None
show_letter = False
visited_objects = set()
room_opened = False
current_room = "room1"
mat_triggered = False

# room1の調査対象オブジェクト
all_objects = {
    "calendar", "pc", "mirror", "imt", "huku", "kotatsu", "kotatsu2",
    "kotatsubook", "kotatsutea", "tiikawa", "nail", "gomi", "book", "bed"
}

def update():
    global player_x, player_y, player_dir, show_message
    global room_opened, current_room, mat_triggered, show_letter

    old_x, old_y = player_x, player_y

    # キャラ移動
    if pyxel.btn(pyxel.KEY_UP):
        player_y -= 2
        player_dir = "back"
    elif pyxel.btn(pyxel.KEY_DOWN):
        player_y += 2
        player_dir = "front"
    elif pyxel.btn(pyxel.KEY_LEFT):
        player_x -= 2
        player_dir = "left"
    elif pyxel.btn(pyxel.KEY_RIGHT):
        player_x += 2
        player_dir = "right"

    # 画面外に出ないよう制御
    player_x = max(0, min(player_x, 255 - player_size))
    player_y = max(0, min(player_y, 200 - player_size))

    # 当たり判定
    if is_colliding(player_x, player_y):
        player_x, player_y = old_x, old_y

    # Enterキー押下時の挙動
    if pyxel.btnp(pyxel.KEY_RETURN):
        if show_letter:
            show_letter = False
            return
        if show_message == "room_open":
            show_message = None
            room_opened = True
        elif show_message == "mat":
            show_message = None
            if current_room == "room1":
                # room1 → room2 へ移動
                visited_objects.clear()
                current_room = "room2"
                pyxel.images[0].load(0, 0, "assets/room2.png", True)
                pyxel.images[2].load(0, 0, "assets/window.png")
                pyxel.images[1].load(0, 0, "assets/chara_top2.png")
                pyxel.images[1].load(32, 0, "assets/chara_left2.png")
                pyxel.images[1].load(64, 0, "assets/chara_right2.png")
                pyxel.images[1].load(96, 0, "assets/chara_back2.png")
                pyxel.stop()
                pyxel.playm(0, loop=True)
            elif current_room == "room2":
                # room2 → room1 に戻る
                current_room = "room1"
                pyxel.images[0].load(0, 0, "assets/room.png", True)
                pyxel.images[2].load(0, 0, "assets/window.png")
                pyxel.images[1].load(0, 0, "assets/chara_top.png")
                pyxel.images[1].load(32, 0, "assets/chara_left.png")
                pyxel.images[1].load(64, 0, "assets/chara_right.png")
                pyxel.images[1].load(96, 0, "assets/chara_back.png")
                pyxel.stop()
                pyxel.playm(0, loop=True)
            mat_triggered = False
            return
        elif show_message:
            if show_message == "left_corner":
                show_message = None
                show_letter = True
                return
            show_message = None
            if not room_opened and all_objects <= visited_objects:
                show_message = "room_open"
                pyxel.play(1, 2)
        else:
            # room1調査
            if current_room == "room1":
                for obj in all_objects:
                    if check_near(player_x, player_y, obj):
                        visited_objects.add(obj)
                        show_message = obj
                        return
            # room2調査
            if current_room == "room2":
                for obj in ["cake", "left_corner", "bottom_table", "right_corner"]:
                    if check_near(player_x, player_y, obj):
                        show_message = obj
                        return
            # room1で部屋が開いた後のマット
            if room_opened and check_near(player_x, player_y, "mat") and not mat_triggered:
                show_message = "mat"
                mat_triggered = True

def is_colliding(x, y):
    px, py = x + player_size // 2, y + player_size // 2
    if current_room == "room1":
        collision_areas = [
            (0, 0, 255, 50),
            (0, 70, 38, 155),
            (92, 94, 170, 160),
            (127, 32, 190, 70),
            (215, 32, 223, 96),
            (223, 96, 255, 112),
            (38, 152, 70, 200),
        ]
    elif current_room == "room2":
        collision_areas = [
            (0, 0, 255, 90),  # 壁
            (100, 0, 160, 130),  # 中央ケーキ
            (0, 0, 70, 115),  # 左上
            (0, 160, 155, 200),  # 下側
            (200, 0, 255, 125),  # 右上
        ]
    else:
        return False
    return any(x1 <= px <= x2 and y1 <= py <= y2 for x1, y1, x2, y2 in collision_areas)

def check_near(x, y, obj):
    px, py = x + player_size // 2, y + player_size // 2
    area = {
        # room1
        "calendar": (195, 30, 208, 53),
        "pc": (160, 40, 190, 75),
        "mirror": (60, 30, 70, 52),
        "imt": (20, 30, 40, 53),
        "huku": (83, 30, 98, 52),
        "kotatsu": (87, 110, 100, 175),
        "kotatsu2": (100, 143, 160, 162),
        "kotatsubook": (150, 120, 173, 148),
        "kotatsutea": (120, 90, 150, 120),
        "tiikawa": (0, 80, 42, 110),
        "nail": (0, 111, 42, 130),
        "gomi": (0, 143, 40, 150),
        "book": (43, 150, 80, 180),
        "bed": (210, 30, 250, 115),
        "mat": (200, 160, 255, 190),
        # room2
        "cake": (110, 0, 170, 140),
        "left_corner": (0, 0, 75, 125),  # 左
        "bottom_table": (0, 153, 160, 200),  # 下
        "right_corner": (200, 0, 255, 130),  # 右
    }.get(obj, (0, 0, 0, 0))
    x1, y1, x2, y2 = area
    return x1 <= px <= x2 and y1 <= py <= y2

def draw():
    pyxel.cls(0)
    pyxel.blt(0, 0, 0, 0, 0, 255, 200, 0)
    u_table = {"front": 0, "left": 32, "right": 64, "back": 96}
    u = u_table[player_dir]
    pyxel.blt(player_x, player_y, 1, u, 0, 32, 32, 0)

    if show_message:
        pyxel.blt(17, 150, 2, 0, 0, 220, 35, 0)
        msg_table = {
            "cake": "おおきなバースデーケーキ！ロウソクがゆれてる…！",
            "left_corner": "可愛い棚だ！あれ？手紙がはさまってる...？",
            "bottom_table": "おいしそうなごちそうが並んでる！全部たべたい〜！",
            "right_corner": "みんなからのプレゼントとぬいぐるみがいっぱいだ！",
            "calendar": "今日は5月26日！わたしのたんじょうび！",
            "pc": "前回の配信は3か月前...サブスクしてくれてる人に土下座",
            "mirror": "わたしは １４歳天使・・・わたしは １４歳天使・・・",
            "imt": "IMT（いちのせちゃんは　まじ　てんし）",
            "huku": "次のコスプレは 地獄少女の　えんまあいちゃん！",
            "kotatsu": "銀座のスタンダードプロダクツで小物買ったなあ...",
            "kotatsu2": "早く土曜日にならないかな　ゆきくんに会いたいな！",
            "kotatsubook": "わたしの彼氏（吉沢亮）、復帰してくれて嬉しいな",
            "kotatsutea": "紅茶に見せかけて実は甘酒...わたしの甘酒最強！",
            "tiikawa": "ここはちいちゃんコーナー　もう置く場所ないよ・・・",
            "nail": "誕生日ネイルはセボンスターみたいなキラキラにする！",
            "gomi": "ガサゴソ..あ！昨日間違えて捨てたパン！パクッ！",
            "book": "スミマセン、これでも片づけたほうなんです、ハイ...",
            "bed": "ふかふかのベッド。でも今日は起きる！",
            "room_open": "右下の部屋が開いたようだ...",
            "mat": "地下への通路がある！いってみよう！"
        }
        # room2のマットは特別メッセージ
        if show_message == "mat" and current_room == "room2":
            pyxel.text(22, 160, "１階に戻ろう！", 7, font)
        else:
            pyxel.text(22, 160, msg_table.get(show_message, ""), 7, font)

    if show_letter:
        pyxel.blt((255 - 200) // 2, (200 - 141) // 2, 2, 0, 35, 200, 141, 0)

pyxel.run(update, draw)
