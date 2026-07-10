import asyncio
import json
import os
import random
import sqlite3
from datetime import datetime
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from PIL import Image
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


BASE_DIR = Path(__file__).resolve().parent
START_IMAGE = BASE_DIR / "assets" / "fish_2026-07-09T13-36-10_92.jpg"
PERCH_IMAGE = BASE_DIR / "assets" / "perch.png"
PIKE_IMAGE = BASE_DIR / "assets" / "pike.png"
ZANDER_IMAGE = BASE_DIR / "assets" / "fish_2026-07-08T17-49-04.jpg"
ASP_IMAGE = BASE_DIR / "assets" / "fish_2026-07-08T17-49-05.jpg"
BREAM_IMAGE = BASE_DIR / "assets" / "fish_2026-07-08T18-16-08.jpg"
BREAKAWAY_IMAGE = BASE_DIR / "assets" / "fish_2026-07-08T18-40-48.jpg"
GOLD_FISH_IMAGE = BASE_DIR / "assets" / "fish_2026-07-08T18-40-49.jpg"
CRUCIAN_IMAGE = BASE_DIR / "assets" / "fish_2026-07-09T11-03-19.jpg"
CHEBAK_IMAGE = BASE_DIR / "assets" / "fish_2026-07-09T11-05-43_72.jpg"
CATFISH_IMAGE = BASE_DIR / "assets" / "fish_2026-07-09T11-03-20.jpg"
BURBOT_IMAGE = BASE_DIR / "assets" / "fish_2026-07-09T11-34-04_78.jpg"
BOOT_IMAGE = BASE_DIR / "assets" / "fish_2026-07-09T11-34-04_79.jpg"
TROUT_IMAGE = BASE_DIR / "assets" / "fish_2026-07-09T13-16-09_84.jpg"
SMELT_IMAGE = BASE_DIR / "assets" / "fish_2026-07-09T13-16-19_86.jpg"
GRAYLING_IMAGE = BASE_DIR / "assets" / "fish_2026-07-09T13-16-20_87.jpg"
PERCH_CUSTOM_EMOJI_ID = "5364182636786921265"
PIKE_CUSTOM_EMOJI_ID = "5366383064496775731"
ZANDER_CUSTOM_EMOJI_ID = "5364159564222604584"
ASP_CUSTOM_EMOJI_ID = "5364323696397817808"
BREAM_CUSTOM_EMOJI_ID = "5366271807663941546"
GOLD_FISH_CUSTOM_EMOJI_ID = "5364311210927890407"
CRUCIAN_CUSTOM_EMOJI_ID = "5368818109090142464"
CHEBAK_CUSTOM_EMOJI_ID = "5368553625004058897"
CATFISH_CUSTOM_EMOJI_ID = "5366235540960094823"
BURBOT_CUSTOM_EMOJI_ID = "5366371042883313078"
BOOT_CUSTOM_EMOJI_ID = "5368849758704147356"
TROUT_CUSTOM_EMOJI_ID = "5366054430779156499"
SMELT_CUSTOM_EMOJI_ID = "5366138603548221529"
GRAYLING_CUSTOM_EMOJI_ID = "5366291281045660683"
FORMATTED_MESSAGE_PATH = BASE_DIR / "work" / "last_formatted_message.json"
FORMATTED_MESSAGES_LOG_PATH = BASE_DIR / "work" / "formatted_messages.jsonl"
PHOTO_FILE_IDS_PATH = BASE_DIR / "work" / "photo_file_ids.json"
STATS_DB_PATH = BASE_DIR / "stats.sqlite"
CATCH_BACKGROUND_IMAGE = BASE_DIR / "assets" / "catch" / "background.png"
CATCH_FISH_DIR = BASE_DIR / "assets" / "catch" / "fish"
MAX_ATTEMPTS = 5
CATCH_CARD_SCALE = 0.34
CATCH_CARD_MARGIN = 8
CATCH_RESERVED_AREAS = [
    (40, 80, 560, 180),
    (900, 0, 1050, 155),
    (45, 940, 450, 1045),
]
CATCH_CARD_CANDIDATES = [
    {"center_x": 735, "center_y": 410, "face": "right", "angle": 3},
    {"center_x": 300, "center_y": 635, "face": "left", "angle": -2},
    {"center_x": 705, "center_y": 725, "face": "right", "angle": -3},
    {"center_x": 305, "center_y": 330, "face": "left", "angle": -4},
    {"center_x": 760, "center_y": 280, "face": "right", "angle": 2},
    {"center_x": 285, "center_y": 445, "face": "left", "angle": 1},
    {"center_x": 770, "center_y": 575, "face": "right", "angle": -2},
    {"center_x": 540, "center_y": 300, "face": "right", "angle": 2},
    {"center_x": 520, "center_y": 610, "face": "left", "angle": -2},
    {"center_x": 315, "center_y": 625, "face": "left", "angle": -2},
    {"center_x": 430, "center_y": 600, "face": "right", "angle": 2},
    {"center_x": 840, "center_y": 790, "face": "right", "angle": 4},
    {"center_x": 215, "center_y": 805, "face": "left", "angle": -3},
    {"center_x": 760, "center_y": 245, "face": "right", "angle": 0},
    {"center_x": 500, "center_y": 845, "face": "left", "angle": -2},
    {"center_x": 850, "center_y": 660, "face": "right", "angle": 3},
    {"center_x": 230, "center_y": 450, "face": "left", "angle": -2},
    {"center_x": 600, "center_y": 500, "face": "right", "angle": 1},
    {"center_x": 560, "center_y": 255, "face": "right", "angle": 0},
    {"center_x": 885, "center_y": 285, "face": "right", "angle": 2},
    {"center_x": 520, "center_y": 820, "face": "left", "angle": -2},
    {"center_x": 860, "center_y": 535, "face": "right", "angle": 2},
    {"center_x": 330, "center_y": 875, "face": "left", "angle": -3},
    {"center_x": 555, "center_y": 555, "face": "right", "angle": 0},
]
CATCH_FIGMA_WIDTHS = {
    "slot_1": 850,
    "slot_2": 1300,
    "slot_3": 1150,
    "slot_4": 1000,
    "slot_5": 1050,
    "slot_7": 700,
    "slot_8": 750,
    "slot_9": 650,
    "slot_10": 1450,
    "slot_11": 1100,
    "slot_12": 750,
    "slot_13": 950,
    "slot_14": 500,
    "slot_15": 800,
}

START_TEXT = """<b>Привет рыбакам! 

Закидывайте удочку и любуйтесь уловом</b> 🎣"""

PERCH_TEXT = """<b>Вы встретили стайку окуней</b> <tg-emoji emoji-id="5364182636786921265">🤩</tg-emoji> <tg-emoji emoji-id="5364182636786921265">🤩</tg-emoji> <tg-emoji emoji-id="5364182636786921265">🤩</tg-emoji>

<i>Они же полосатики, горбачи и матросики </i>

Окунь обитает почти во всех пресных водоёмах и речках. Мало того, окунь живёт и почти на всех континентах. Когда этого мелкого хищника завезли в Австралию, то он вообще стал угрозой сразу для 14 видов рыб
"""

PIKE_TEXT = """<b>Вы поймали щуку! </b><tg-emoji emoji-id="5366383064496775731">🤩</tg-emoji>
<i>
Будьте осторожны, зубов у неё больше, чем у вас желаний </i>

Это настоящий коварный хищник! К тому же, огромный — щука вырастает <b>до 1,5 метров в длину</b>. Когда щука не занята приключениями с Емелей, таится в водных зарослях и внезапно нападает на мирных рыб 🍴 
"""

ZANDER_TEXT = """<b>Вот это удача! Судак на крючке </b><b><tg-emoji emoji-id="5364159564222604584">🤩</tg-emoji></b> 

<i>Бойкий хищник не ожидал стать сегодня добычей </i>

Судак не любит заболоченной водицы — ему подавай только водоёмы с хорошим уровнем кислорода. Увидеть и даже услышать его на мелководье<b> можно ночью</b>, он будет бурно плескаться во время охоты. А ещё у судака в темноте светятся глаза. <i>Страшно? </i><i><span class="tg-spoiler">Пескарям тоже</span></i>"""

ASP_TEXT = """<b>В награду за терпение — красавец жерех </b><tg-emoji emoji-id="5364323696397817808">🤩</tg-emoji>

<i>Огромная, но быстрая и внимательная рыба </i>

Достигает 120 см в длину и 12 кг веса. Любит речки и водоёмы с множеством укрытий. Охота на жереха может стать настоящим испытанием — он очень осторожен, быстр и силён"""

BREAM_TEXT = """Держите леща! <tg-emoji emoji-id="5366271807663941546">🤩</tg-emoji>

<i>Горбатый плоский лещ очень осторожен </i>

Юные лещики — серебристые, а взрослые — бронзовые и золотистые. Любят тихую размеренную жизнь — непроточную воду или речки с медленным течением. <b>Прибираются на дне</b>, вычищая всё на своём пути"""

BREAKAWAY_TEXT = """Сорвалась! 😰"""

GOLD_FISH_TEXT = """Это же ЗОЛОТАЯ РЫБКА 🤩 

<tg-emoji emoji-id="5364311210927890407">🤩</tg-emoji> Скорее загадайте желание и отпустите её. Только НИ СЛОВА про «морскую владычицу», у Золотой Рыбки уже была одна неприятная история с этим"""

CRUCIAN_TEXT = """<b>Вам попался карась! </b><tg-emoji emoji-id="5368818109090142464">🤩</tg-emoji>

<i>Выживает даже в самой илистой воде </i>

Карась — это ближайший <b>родственник золотой рыбки! </b>У коренных народов Дальнего Востока он занимает почётное место священного животного. И даже помогает шаманам предсказывать погоду"""

CHEBAK_TEXT = """<b>Кто это у нас? Чебак! </b><tg-emoji emoji-id="5368553625004058897">🤩</tg-emoji> 

<i>Он же — сибирская плотва</i>

Очень распространённая рыба в реках Урала и Сибири. Единственный вид плотвы, который добывают в промышленных масштабах. Интересно, что само <b>название «чебак» — народное</b>, и в одних районах так называют плотву, в других — елец, а иногда — и крупную белую рыбу"""

CATFISH_TEXT = """<b>Тянем-потянем! Сом на крючке! </b><b><tg-emoji emoji-id="5366235540960094823">🤩</tg-emoji></b>

<i>Речной гигант с усами </i>

Только представьте! Самый большой пойманный европейский сом весил <b>135 кг</b>, а его брат меконгский гигантский сом — <b>293 кг</b>. Эта чудо-юдо рыба может дожить <b>до 80 лет</b>. Во Франции сомы научились охотиться на голубей. А вот легенды о нападении на людей — просто легенды"""

BURBOT_TEXT = """<tg-emoji emoji-id="5366371042883313078">🤩</tg-emoji> <b>На мели мы налима лениво ловили, меняли налима вы мне на линя</b>

<i>О любви не меня ли вы мило молили и в туманы лимана манили меня?</i>

Похож и на сома, и на угря. Но на самом деле это единственный пресноводный родственник трески. Любит <b>холодные и чистые водоёмы</b>. Настолько он вдохновляется холодом, что даже брачный сезон у налимов зимой"""

BOOT_TEXT = """<b>Ой, это всего лишь старый башмак</b> <tg-emoji emoji-id="5368849758704147356">🤩</tg-emoji>

<i>Всегда забирайте свой мусор с водоёмов! Рыбкам плохо в грязных речках и озёрах!</i>"""

TROUT_TEXT = """<b>Ммммм! Форель </b><tg-emoji emoji-id="5366054430779156499">🤩</tg-emoji><b> </b>

<i>В нашем случае — пресноводная кумжа</i>

Её можно встретить в ручьях, озёрах и реках. Кумжа не согласна жить в грязных водоёмах — её называют <b>«индикатором» чистого водоёма</b>. Может менять окраску из-за условий или просто настроения. И даже мясо у форели бывает и розовое, и белое — зависит от питания

Некоторые виды форели занесены в Красную книгу России!"""

SMELT_TEXT = """<b>Корюшка пошла! </b><tg-emoji emoji-id="5366138603548221529">🤩</tg-emoji>

<i>Вы поймали настоящий символ Петербурга</i>

Рыбка-малышка. Её озёрный вид вырастает всего до 10 см, европейский — до 20 см, а вот сибирский брат до 35 см. Корюшка <b>пахнет огурцом </b>и арбузной коркой. Хоть рыбка и мала, но она настоящий хищник!"""

GRAYLING_TEXT = """<b>Эффектно появляется хариус! </b><tg-emoji emoji-id="5366291281045660683">🤩</tg-emoji> 

<i>Пресноводный северный родственник лососей </i>

Очень красивая рыбка! Хариус даже <b>попал на герб </b>небольшого округа в Иркутской области. Любит холодную и чистую воду. Для рыбаков это непростая добыча — хариус осторожен и внимателен"""

FISH_SLOTS = {
    "slot_1": {
        "text": PERCH_TEXT,
        "image": PERCH_IMAGE,
        "custom_emoji_id": PERCH_CUSTOM_EMOJI_ID,
        "share_name": "окуня",
    },
    "slot_2": {
        "text": PIKE_TEXT,
        "image": PIKE_IMAGE,
        "custom_emoji_id": PIKE_CUSTOM_EMOJI_ID,
        "share_name": "щуку",
    },
    "slot_3": {
        "text": ZANDER_TEXT,
        "image": ZANDER_IMAGE,
        "custom_emoji_id": ZANDER_CUSTOM_EMOJI_ID,
        "share_name": "судака",
    },
    "slot_4": {
        "text": ASP_TEXT,
        "image": ASP_IMAGE,
        "custom_emoji_id": ASP_CUSTOM_EMOJI_ID,
        "share_name": "жереха",
    },
    "slot_5": {
        "text": BREAM_TEXT,
        "image": BREAM_IMAGE,
        "custom_emoji_id": BREAM_CUSTOM_EMOJI_ID,
        "share_name": "леща",
    },
    "slot_6": {
        "text": BREAKAWAY_TEXT,
        "image": BREAKAWAY_IMAGE,
        "custom_emoji_id": None,
        "keep_wave": True,
    },
    "slot_7": {
        "text": GOLD_FISH_TEXT,
        "image": GOLD_FISH_IMAGE,
        "custom_emoji_id": GOLD_FISH_CUSTOM_EMOJI_ID,
        "wish": True,
        "share_name": "золотую рыбку",
    },
    "slot_8": {
        "text": CRUCIAN_TEXT,
        "image": CRUCIAN_IMAGE,
        "custom_emoji_id": CRUCIAN_CUSTOM_EMOJI_ID,
        "share_name": "карася",
    },
    "slot_9": {
        "text": CHEBAK_TEXT,
        "image": CHEBAK_IMAGE,
        "custom_emoji_id": CHEBAK_CUSTOM_EMOJI_ID,
        "share_name": "чебака",
    },
    "slot_10": {
        "text": CATFISH_TEXT,
        "image": CATFISH_IMAGE,
        "custom_emoji_id": CATFISH_CUSTOM_EMOJI_ID,
        "share_name": "сома",
    },
    "slot_11": {
        "text": BURBOT_TEXT,
        "image": BURBOT_IMAGE,
        "custom_emoji_id": BURBOT_CUSTOM_EMOJI_ID,
        "share_name": "налима",
    },
    "slot_12": {
        "text": BOOT_TEXT,
        "image": BOOT_IMAGE,
        "custom_emoji_id": BOOT_CUSTOM_EMOJI_ID,
        "share_name": "старый башмак",
    },
    "slot_13": {
        "text": TROUT_TEXT,
        "image": TROUT_IMAGE,
        "custom_emoji_id": TROUT_CUSTOM_EMOJI_ID,
        "share_name": "форель",
    },
    "slot_14": {
        "text": SMELT_TEXT,
        "image": SMELT_IMAGE,
        "custom_emoji_id": SMELT_CUSTOM_EMOJI_ID,
        "share_name": "корюшку",
    },
    "slot_15": {
        "text": GRAYLING_TEXT,
        "image": GRAYLING_IMAGE,
        "custom_emoji_id": GRAYLING_CUSTOM_EMOJI_ID,
        "share_name": "хариуса",
    },
}


def format_attempt_word(count: int) -> str:
    if count == 1:
        return "раз"
    if 2 <= count <= 4:
        return "раза"
    return "раз"


def get_admin_ids() -> set[int]:
    admin_ids = os.getenv("ADMIN_USER_IDS", "").strip()
    if not admin_ids:
        return set()

    return {
        int(admin_id.strip())
        for admin_id in admin_ids.split(",")
        if admin_id.strip().isdigit()
    }


def init_stats_db() -> None:
    with sqlite3.connect(STATS_DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_seen_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def record_user(user_id: int | None) -> None:
    if user_id is None:
        return

    now = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(STATS_DB_PATH) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO users (user_id, first_seen_at)
            VALUES (?, ?)
            """,
            (user_id, now),
        )


def record_event(user_id: int | None, event_name: str) -> None:
    if user_id is None:
        return

    record_user(user_id)
    now = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(STATS_DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO events (user_id, event_name, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, event_name, now),
        )


def count_events(event_name: str) -> int:
    with sqlite3.connect(STATS_DB_PATH) as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM events WHERE event_name = ?",
            (event_name,),
        ).fetchone()
    return row[0]


def count_users() -> int:
    with sqlite3.connect(STATS_DB_PATH) as connection:
        row = connection.execute("SELECT COUNT(*) FROM users").fetchone()
    return row[0]


def load_photo_file_ids() -> dict[str, str]:
    if not PHOTO_FILE_IDS_PATH.exists():
        return {}

    try:
        return json.loads(PHOTO_FILE_IDS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_photo_file_ids(photo_file_ids: dict[str, str]) -> None:
    PHOTO_FILE_IDS_PATH.parent.mkdir(exist_ok=True)
    PHOTO_FILE_IDS_PATH.write_text(
        json.dumps(photo_file_ids, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def cache_message_photo_file_id(
    context: ContextTypes.DEFAULT_TYPE,
    image_path: Path,
    message,
) -> None:
    if not message or not getattr(message, "photo", None):
        return

    photo_file_ids = context.bot_data.setdefault("photo_file_ids", {})
    photo_file_ids[str(image_path)] = message.photo[-1].file_id
    save_photo_file_ids(photo_file_ids)


def get_warmup_images() -> list[tuple[str, Path]]:
    images = [("Стартовая картинка", START_IMAGE)]
    for slot_id, slot in FISH_SLOTS.items():
        images.append((slot.get("share_name", slot_id), slot["image"]))
    return images


async def reply_cached_photo(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    image_path: Path,
    caption: str,
    reply_markup: InlineKeyboardMarkup,
):
    photo_file_ids = context.bot_data.setdefault("photo_file_ids", {})
    cached_file_id = photo_file_ids.get(str(image_path))

    if cached_file_id:
        try:
            return await context.bot.send_photo(
                chat_id=chat_id,
                photo=cached_file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        except BadRequest:
            photo_file_ids.pop(str(image_path), None)
            save_photo_file_ids(photo_file_ids)

    with image_path.open("rb") as photo:
        message = await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    cache_message_photo_file_id(context, image_path, message)
    return message


async def edit_cached_photo(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    image_path: Path,
    caption: str,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    photo_file_ids = context.bot_data.setdefault("photo_file_ids", {})
    cached_file_id = photo_file_ids.get(str(image_path))
    media_photo = cached_file_id

    if cached_file_id:
        try:
            message = await query.edit_message_media(
                media=InputMediaPhoto(
                    media=media_photo,
                    caption=caption,
                    parse_mode="HTML",
                ),
                reply_markup=reply_markup,
            )
            cache_message_photo_file_id(context, image_path, message)
            return
        except BadRequest as error:
            if "Message is not modified" in str(error):
                raise
            photo_file_ids.pop(str(image_path), None)
            save_photo_file_ids(photo_file_ids)

    with image_path.open("rb") as photo:
        message = await query.edit_message_media(
            media=InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML"),
            reply_markup=reply_markup,
        )
    cache_message_photo_file_id(context, image_path, message)


def build_caption(fish_text: str, attempts_used: int) -> str:
    attempts_left = MAX_ATTEMPTS - attempts_used

    if attempts_left > 0:
        attempts_text = (
            f"Вы можете попытаться еще {attempts_left} "
            f"{format_attempt_word(attempts_left)}"
        )
    else:
        attempts_text = "Попытки закончились"

    return f"{fish_text.rstrip()}\n\n<blockquote>{attempts_text}</blockquote>"


def build_share_url(caught_slots: set[str], bot_username: str | None) -> str:
    caught_fish = [
        FISH_SLOTS[slot_id]["share_name"]
        for slot_id in get_share_slot_ids(caught_slots)
    ]
    catch_text = ", ".join(caught_fish) if caught_fish else "пока ничего"
    bot_url = f"https://t.me/{bot_username}" if bot_username else ""
    text = f"Я поймал на рыбалке {catch_text} 🐟"
    text = f"{text}\n\nА каких рыб поймаешь ты?"

    return (
        "https://t.me/share/url"
        f"?url={quote(bot_url, safe='')}"
        f"&text={quote(text, safe='')}"
    )


def get_share_slot_ids(
    caught_slots: set[str],
    caught_order: list[str] | None = None,
) -> list[str]:
    ordered_slots = caught_order or list(FISH_SLOTS)
    return [
        slot_id
        for slot_id in ordered_slots
        if slot_id in caught_slots and not FISH_SLOTS[slot_id].get("keep_wave")
    ]


def expand_rect(rect: tuple[int, int, int, int], margin: int) -> tuple[int, int, int, int]:
    left, top, right, bottom = rect
    return (left - margin, top - margin, right + margin, bottom + margin)


def rects_intersect(
    first: tuple[int, int, int, int],
    second: tuple[int, int, int, int],
) -> bool:
    return not (
        first[2] <= second[0]
        or first[0] >= second[2]
        or first[3] <= second[1]
        or first[1] >= second[3]
    )


def rect_fits_card(rect: tuple[int, int, int, int], card_size: tuple[int, int]) -> bool:
    width, height = card_size
    return rect[0] >= 0 and rect[1] >= 0 and rect[2] <= width and rect[3] <= height


def find_catch_card_position(
    fish: Image.Image,
    occupied_rects: list[tuple[int, int, int, int]],
    card_size: tuple[int, int],
) -> tuple[Image.Image, tuple[int, int, int, int], tuple[int, int]] | None:
    for scale in (1.0, 0.92, 0.84, 0.76, 0.68, 0.6, 0.52, 0.44, 0.36):
        scaled_fish = fish
        if scale != 1.0:
            scaled_fish = fish.resize(
                (
                    round(fish.width * scale),
                    round(fish.height * scale),
                ),
                Image.Resampling.LANCZOS,
            )

        for layout in CATCH_CARD_CANDIDATES:
            placed_fish = scaled_fish
            if layout["face"] == "right":
                placed_fish = placed_fish.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if layout["angle"]:
                placed_fish = placed_fish.rotate(
                    layout["angle"],
                    expand=True,
                    resample=Image.Resampling.BICUBIC,
                )

            x = round(layout["center_x"] - placed_fish.width / 2)
            y = round(layout["center_y"] - placed_fish.height / 2)
            rect = (x, y, x + placed_fish.width, y + placed_fish.height)
            padded_rect = expand_rect(rect, CATCH_CARD_MARGIN)

            if not rect_fits_card(rect, card_size):
                continue
            if any(rects_intersect(padded_rect, occupied) for occupied in occupied_rects):
                continue

            return placed_fish, padded_rect, (x, y)

    return None


def build_catch_card(caught_slots: set[str], caught_order: list[str] | None) -> BytesIO:
    slot_ids = get_share_slot_ids(caught_slots, caught_order)[:MAX_ATTEMPTS]
    slot_ids = sorted(
        slot_ids,
        key=lambda slot_id: CATCH_FIGMA_WIDTHS.get(slot_id, 0),
        reverse=True,
    )
    card = Image.open(CATCH_BACKGROUND_IMAGE).convert("RGBA")
    occupied_rects = [
        expand_rect(rect, CATCH_CARD_MARGIN)
        for rect in CATCH_RESERVED_AREAS
    ]

    for slot_id in slot_ids:
        fish_path = CATCH_FISH_DIR / f"{slot_id}.png"
        if not fish_path.exists():
            continue

        fish = Image.open(fish_path).convert("RGBA")
        figma_width = CATCH_FIGMA_WIDTHS.get(slot_id, fish.width)
        target_width = round(figma_width * CATCH_CARD_SCALE)
        target_height = round(fish.height * target_width / fish.width)
        fish = fish.resize((target_width, target_height), Image.Resampling.LANCZOS)

        position = find_catch_card_position(fish, occupied_rects, card.size)
        if position is None:
            continue

        placed_fish, occupied_rect, point = position
        occupied_rects.append(occupied_rect)
        card.alpha_composite(placed_fish, point)

    output = BytesIO()
    output.name = "catch.png"
    card.convert("RGB").save(output, format="PNG")
    output.seek(0)
    return output


def build_keyboard(
    caught_slots: set[str] | None = None,
    slot_order: list[str] | None = None,
    show_end_actions: bool = False,
    share_url: str | None = None,
) -> InlineKeyboardMarkup:
    caught_slots = caught_slots or set()
    slot_order = slot_order or list(FISH_SLOTS)

    buttons = []
    for slot_id in slot_order:
        slot = FISH_SLOTS[slot_id]
        is_caught = slot_id in caught_slots
        custom_emoji_id = slot.get("custom_emoji_id")
        buttons.append(
            InlineKeyboardButton(
                " " if is_caught else "🌊",
                callback_data=slot_id,
                api_kwargs=(
                    {"icon_custom_emoji_id": custom_emoji_id}
                    if is_caught and custom_emoji_id
                    else None
                ),
            )
        )

    keyboard = [
        buttons[index : index + 5]
        for index in range(0, len(buttons), 5)
    ]

    if show_end_actions:
        keyboard.insert(
            0,
            [
                InlineKeyboardButton(
                    "🎣 Сыграть ещё раз",
                    callback_data="play_again",
                ),
            ],
        )
        keyboard.insert(
            1,
            [
                InlineKeyboardButton(
                    "Похвастаться уловом 🐟",
                    callback_data="share_catch",
                ),
            ],
        )

    return InlineKeyboardMarkup(keyboard)


def build_share_keyboard(share_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Отправить улов 🐟",
                    url=share_url,
                )
            ]
        ]
    )


def build_wish_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Загадать желание",
                    callback_data="make_wish",
                    api_kwargs={"icon_custom_emoji_id": GOLD_FISH_CUSTOM_EMOJI_ID},
                )
            ]
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    record_event(update.effective_user.id, "game_started")

    slot_order = list(FISH_SLOTS)
    random.shuffle(slot_order)

    context.user_data["caught_slots"] = set()
    context.user_data["attempted_slots"] = set()
    context.user_data["current_slot"] = None
    context.user_data["attempts_used"] = 0
    context.user_data["slot_order"] = slot_order
    context.user_data["caught_order"] = []
    context.user_data["game_finished_recorded"] = False
    context.user_data["catch_shared"] = False

    await reply_cached_photo(
        context=context,
        chat_id=update.message.chat_id,
        image_path=START_IMAGE,
        caption=START_TEXT,
        reply_markup=build_keyboard(slot_order=slot_order),
    )


async def choose_slot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    caught_slots = context.user_data.setdefault("caught_slots", set())
    caught_order = context.user_data.setdefault("caught_order", [])
    attempted_slots = context.user_data.setdefault("attempted_slots", set())
    attempts_used = context.user_data.setdefault("attempts_used", 0)
    slot_order = context.user_data.setdefault("slot_order", list(FISH_SLOTS))
    is_new_slot = query.data not in attempted_slots

    if is_new_slot and attempts_used >= MAX_ATTEMPTS:
        await query.answer()
        return

    await query.answer()

    if is_new_slot:
        attempted_slots.add(query.data)
        attempts_used += 1
        context.user_data["attempts_used"] = attempts_used

        if (
            attempts_used >= MAX_ATTEMPTS
            and not context.user_data.get("game_finished_recorded")
        ):
            record_event(query.from_user.id, "game_finished")
            context.user_data["game_finished_recorded"] = True

    context.user_data["current_slot"] = query.data

    slot = FISH_SLOTS.get(query.data)
    if not slot:
        return

    if not slot.get("keep_wave"):
        caught_slots.add(query.data)
        if query.data not in caught_order:
            caught_order.append(query.data)

    image_path = slot["image"]
    text = (
        slot["text"]
        if slot.get("wish")
        else build_caption(slot["text"], attempts_used)
    )
    show_end_actions = attempts_used >= MAX_ATTEMPTS
    share_url = build_share_url(
        caught_slots,
        context.bot_data.get("bot_username"),
    )
    reply_markup = (
        build_wish_keyboard()
        if slot.get("wish")
        else build_keyboard(
            caught_slots,
            slot_order,
            show_end_actions,
            share_url,
        )
    )

    try:
        await edit_cached_photo(
            query=query,
            context=context,
            image_path=image_path,
            caption=text,
            reply_markup=reply_markup,
        )
    except BadRequest as error:
        if "Message is not modified" not in str(error):
            raise


async def make_wish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    caught_slots = context.user_data.setdefault("caught_slots", set())
    attempts_used = context.user_data.setdefault("attempts_used", 0)
    slot_order = context.user_data.setdefault("slot_order", list(FISH_SLOTS))
    text = build_caption("Ваш запрос принят!\n\nПродолжаем рыбалку", attempts_used)
    show_end_actions = attempts_used >= MAX_ATTEMPTS
    share_url = build_share_url(
        caught_slots,
        context.bot_data.get("bot_username"),
    )

    try:
        await edit_cached_photo(
            query=query,
            context=context,
            image_path=GOLD_FISH_IMAGE,
            caption=text,
            reply_markup=build_keyboard(
                caught_slots,
                slot_order,
                show_end_actions,
                share_url,
            ),
        )
    except BadRequest as error:
        if "Message is not modified" not in str(error):
            raise


async def play_again(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    record_event(query.from_user.id, "play_again")
    record_event(query.from_user.id, "game_started")
    should_send_new_message = context.user_data.get("catch_shared", False)

    slot_order = list(FISH_SLOTS)
    random.shuffle(slot_order)

    context.user_data["caught_slots"] = set()
    context.user_data["attempted_slots"] = set()
    context.user_data["current_slot"] = None
    context.user_data["attempts_used"] = 0
    context.user_data["slot_order"] = slot_order
    context.user_data["caught_order"] = []
    context.user_data["game_finished_recorded"] = False
    context.user_data["catch_shared"] = False

    if should_send_new_message:
        try:
            await query.message.delete()
        except BadRequest:
            pass

        await reply_cached_photo(
            context=context,
            chat_id=query.message.chat_id,
            image_path=START_IMAGE,
            caption=START_TEXT,
            reply_markup=build_keyboard(slot_order=slot_order),
        )
        return

    try:
        await edit_cached_photo(
            query=query,
            context=context,
            image_path=START_IMAGE,
            caption=START_TEXT,
            reply_markup=build_keyboard(slot_order=slot_order),
        )
    except BadRequest as error:
        if "Message is not modified" not in str(error):
            raise


async def share_catch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    record_event(query.from_user.id, "share_clicked")

    caught_slots = context.user_data.setdefault("caught_slots", set())
    caught_order = context.user_data.setdefault("caught_order", [])
    context.user_data["catch_shared"] = True
    share_url = build_share_url(
        caught_slots,
        context.bot_data.get("bot_username"),
    )
    catch_card = build_catch_card(caught_slots, caught_order)

    await query.message.reply_photo(
        photo=catch_card,
        caption="Готово, можно отправить улов:",
        reply_markup=build_share_keyboard(share_url),
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_ids = context.bot_data.get("admin_ids", set())
    user_id = update.effective_user.id

    if admin_ids and user_id not in admin_ids:
        await update.message.reply_text("Эта команда только для администратора.")
        return

    await update.message.reply_text(
        "Статистика рыбалки:\n\n"
        f"Пользователей: {count_users()}\n"
        f"Игр начато: {count_events('game_started')}\n"
        f"Дошли до конца: {count_events('game_finished')}\n"
        f"Сыграли снова: {count_events('play_again')}\n"
        f"Нажали «Похвастаться уловом»: {count_events('share_clicked')}"
    )


async def warmup_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_ids = context.bot_data.get("admin_ids", set())
    user_id = update.effective_user.id

    if admin_ids and user_id not in admin_ids:
        await update.message.reply_text("Эта команда только для администратора.")
        return

    await update.message.reply_text(
        "Начинаю прогрев картинок. Сейчас пришлю служебные изображения."
    )

    photo_file_ids = context.bot_data.setdefault("photo_file_ids", {})
    sent_count = 0
    skipped_count = 0

    for title, image_path in get_warmup_images():
        cache_key = str(image_path)
        if cache_key in photo_file_ids:
            skipped_count += 1
            continue

        with image_path.open("rb") as photo:
            message = await update.message.reply_photo(
                photo=photo,
                caption=f"Прогрев: {title}",
            )
        cache_message_photo_file_id(context, image_path, message)
        sent_count += 1

    await update.message.reply_text(
        "Прогрев готов.\n\n"
        f"Новых картинок загружено: {sent_count}\n"
        f"Уже были в кэше: {skipped_count}\n\n"
        "Файл для переноса: work/photo_file_ids.json"
    )


async def save_formatted_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.message
    text = message.text or message.caption
    html = message.text_html if message.text else message.caption_html
    entities = message.entities or message.caption_entities or []
    saved_at = datetime.now().isoformat(timespec="seconds")
    photo_path = None

    if not text:
        await message.reply_text(
            "Я не нашёл текст в этом сообщении. Пришлите текст или подпись к картинке."
        )
        return

    if message.photo:
        photo_file = await message.photo[-1].get_file()
        photo_filename = (
            f"fish_{saved_at.replace(':', '-')}_{message.message_id}.jpg"
        )
        photo_path = BASE_DIR / "assets" / photo_filename
        await photo_file.download_to_drive(photo_path)

    custom_emoji_ids = [
        entity.custom_emoji_id
        for entity in entities
        if entity.type == "custom_emoji" and entity.custom_emoji_id
    ]

    data = {
        "saved_at": saved_at,
        "text": text,
        "html": html,
        "photo_path": str(photo_path) if photo_path else None,
        "custom_emoji_ids": custom_emoji_ids,
        "entities": [entity.to_dict() for entity in entities],
    }

    FORMATTED_MESSAGE_PATH.parent.mkdir(exist_ok=True)
    FORMATTED_MESSAGE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with FORMATTED_MESSAGES_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")

    await message.reply_text("Готово, я сохранил форматирование этого сообщения.")


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([])
    bot = await application.bot.get_me()
    application.bot_data["bot_username"] = bot.username
    application.bot_data["admin_ids"] = get_admin_ids()
    application.bot_data["photo_file_ids"] = load_photo_file_ids()


def main() -> None:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "Не найден BOT_TOKEN. Добавьте токен перед запуском бота."
        )

    init_stats_db()

    app = Application.builder().token(token).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats_admin_fp", stats))
    app.add_handler(CommandHandler("warmup_photos_fp", warmup_photos))
    app.add_handler(CallbackQueryHandler(make_wish, pattern="^make_wish$"))
    app.add_handler(CallbackQueryHandler(play_again, pattern="^play_again$"))
    app.add_handler(CallbackQueryHandler(share_catch, pattern="^share_catch$"))
    app.add_handler(CallbackQueryHandler(choose_slot))
    app.add_handler(MessageHandler(~filters.COMMAND, save_formatted_message))

    print("Бот запущен. Остановить можно клавишами Ctrl+C.")
    asyncio.set_event_loop(asyncio.new_event_loop())
    app.run_polling()


if __name__ == "__main__":
    main()
