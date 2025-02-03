import telebot
from yt_dlp import YoutubeDL
import os
import time
import requests

# توكن البوت
bot = telebot.TeleBot("7165480067:AAGqlNq4-zHKOt4IAr1XaBt7Q4wBzgIQZHY")

# دالة لتحميل الفيديو
def download_video(url, message):
    try:
        bot.send_message(message.chat.id, "╮ ❐ يتـم جلـب البيانـات انتظـر قليلاً ...𓅫╰▬▭")

        # إعدادات yt-dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [lambda d: progress_hook(d, message)],  # مؤشر التقدم
            'nocheckcertificate': True,
            'nocolor': True,
            'quiet': True,
            'http_headers': {'User-Agent': 'Mozilla/5.0'},
            'socket_timeout': 60,  # مهلة أطول للشبكة
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        bot.send_message(message.chat.id, f"╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰:\nاسم الفيديو: {info['title']}")

        # رفع الفيديو
        upload_progress(file_name, message)

        # حذف الفيديو بعد الرفع
        os.remove(file_name)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ أثناء التحميل:\n{e}")

# دالة مؤشر التقدم للتحميل
def progress_hook(d, message):
    if d['status'] == 'downloading':
        try:
            percent = float(d['_percent_str'].replace('%', '').strip())
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            progress_bar = create_progress_bar(percent)
            status_message = f"📥 تحميل الفيديو:\n{progress_bar} {percent:.2f}%\n🚀 السرعة: {speed}\n⏳ الوقت المتبقي: {eta}"

            bot.send_message(message.chat.id, status_message)
        except Exception:
            pass

# دالة مؤشر التقدم للرفع
def upload_progress(file_name, message):
    file_size = os.path.getsize(file_name)
    uploaded_size = 0
    chunk_size = 1024 * 1024  # 1 MiB

    with open(file_name, 'rb') as video_file:
        while uploaded_size < file_size:
            chunk = video_file.read(chunk_size)
            uploaded_size += len(chunk)
            percent = (uploaded_size / file_size) * 100
            progress_bar = create_progress_bar(percent)
            status_message = f"⬆️ رفع الفيديو:\nاسم الملف: {os.path.basename(file_name)}\n{progress_bar} {percent:.2f}%\n📦 {uploaded_size / (1024 * 1024):.2f} MiB / {file_size / (1024 * 1024):.2f} MiB"
            try:
                bot.send_message(message.chat.id, status_message)
            except:
                pass
            time.sleep(1)  # محاكاة الرفع

    # إرسال الفيديو
    with open(file_name, "rb") as video:
        bot.send_video(message.chat.id, video)

# دالة لإنشاء progress bar
def create_progress_bar(percent):
    bar_length = 20
    filled_length = int(bar_length * percent / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    return f"[{bar}]"

# أمر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً! ابعتلي رابط يوتيوب وهنزله لك. 🎥")

# معالجة الرسائل
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if url.startswith("http"):
        bot.send_message(message.chat.id, "✅ رابط مقبول! يتم تحميل الفيديو الآن...")
        download_video(url, message)
    else:
        bot.send_message(message.chat.id, "❌ أرسل رابط يوتيوب صحيح!")

# تشغيل البوت مع إعادة المحاولة عند حدوث خطأ
while True:
    try:
        bot.polling(timeout=60, long_polling_timeout=60)
    except requests.exceptions.ReadTimeout:
        print("⚠️ حدثت مهلة اتصال، إعادة المحاولة...")
        time.sleep(5)  # انتظار 5 ثوانٍ ثم إعادة التشغيل
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        time.sleep(5)
