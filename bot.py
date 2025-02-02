import os
import random
import requests
import json
import speedtest
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
import yt_dlp

# توكن البوت الذي حصلت عليه من BotFather
API_ID = "13966124"  # احصل عليه من my.telegram.org
API_HASH = "ffb60460dd6a3e4e087f8b29d3179059"  # احصل عليه من my.telegram.org
BOT_TOKEN = "7165480067:AAGqlNq4-zHKOt4IAr1XaBt7Q4wBzgIQZHY"  # التوكن الذي حصلت عليه من BotFather

# إنشاء عميل Pyrogram
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# مسارات الملفات
BLACKLIST_FILE = "blacklist.txt"
FILE_IDS_FILE = "file_ids.json"

# تحميل القائمة السوداء من ملف
def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "r") as f:
            return [int(line.strip()) for line in f.readlines()]
    return []

# حفظ القائمة السوداء في ملف
def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, "w") as f:
        for user_id in blacklist:
            f.write(f"{user_id}\n")

# تحميل معرفات الملفات من ملف JSON
def load_file_id():
    if os.path.exists(FILE_IDS_FILE):
        with open(FILE_IDS_FILE, "r") as f:
            return json.load(f)
    return {}

# حفظ معرفات الملفات في ملف JSON
def save_file_id(video_id, file_id):
    file_ids = load_file_id()
    file_ids[video_id] = file_id
    with open(FILE_IDS_FILE, "w") as f:
        json.dump(file_ids, f)

# إنشاء اسم ملف عشوائي
def generate_random_filename():
    return f"file_{random.randint(1, 100000)}"

# تعريف الأمر "start"
@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    await message.reply_text(
        "مرحبًا! أنا بوت تحميل مقاطع اليوتيوب كملفات صوتية.\n"
        "استخدم الأمر /يوت متبوعًا باسم الفيديو للبحث والتحميل.\n"
        "يمكنك أيضًا استخدام الأمر /speedtest لقياس سرعة السيرفر."
    )

# تعريف الأمر "speedtest"
@app.on_message(filters.command("speedtest") & filters.private)
async def speedtest_command(client, message: Message):
    await message.reply_text("جارِ قياس سرعة السيرفر...")
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # تحويل إلى Mbps
    upload_speed = st.upload() / 1_000_000  # تحويل إلى Mbps
    await message.reply_text(
        f"نتائج اختبار السرعة:\n"
        f"سرعة التنزيل: {download_speed:.2f} Mbps\n"
        f"سرعة الرفع: {upload_speed:.2f} Mbps"
    )

# تعريف الأمر "يوت"
@app.on_message(filters.command("يوت", "") & filters.private, group=73621362)
async def yot2(client, message: Message):
    loaded_blacklist = load_blacklist()
    if message.from_user.id in loaded_blacklist:
        return
    query = " ".join(message.command[1:])
    downloads_dir = "downloads"
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
    file_ids = load_file_id()
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            video_id = results[0]["id"]
            link = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb = f"{downloads_dir}/{random.randint(1, 100000)}.jpg"
            thumb1 = requests.get(thumbnail, allow_redirects=True)
            open(thumb, "wb").write(thumb1.content)
            duration = results[0]["duration"]
            if video_id in file_ids:
                audio_id = file_ids[video_id]
                await message.reply_audio(
                    audio_id,
                    caption="𝗖𝗵𝗮 ➤ @BotWren",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("تحديثات رين 🎖", url="t.me/BotWren")]]
                    ),
                )
                return
            ydl_opts = {
                "format": "bestaudio[ext=m4a]",
                "outtmpl": f"{downloads_dir}/{generate_random_filename()}.%(ext)s",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=True)
                audio_file = ydl.prepare_filename(info_dict)
                base, ext = os.path.splitext(audio_file)
                new_file = base + ".m4a"
                os.rename(audio_file, new_file)
            rep = "𝗖𝗵𝗮 ➤ @BotWren"
            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60
            sent_message = await message.reply_audio(
                new_file,
                caption=rep,
                thumb=thumb,
                title=title,
                duration=dur,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("تحديثات رين 🎖", url="t.me/BotWren")]]
                ),
            )
            save_file_id(video_id, sent_message.audio.file_id)
            os.remove(new_file)
            os.remove(thumb)
    except Exception as e:
        await message.reply_text(
            "حدثت مشكلة أثناء تحميل الصوت. يرجى المحاولة مرة أخرى لاحقًا."
        )
        print(e)

# تشغيل البوت
app.run()
