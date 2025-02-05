import os
import time
import telebot
from yt_dlp import YoutubeDL
from telebot import types
import pyfiglet

# استبدل 'YOUR_BOT_TOKEN' بالتوكن الخاص بك
bot = telebot.TeleBot('7165480067:AAGqlNq4-zHKOt4IAr1XaBt7Q4wBzgIQZHY')

# دالة لعرض النص مع تأثير الأنيميشن (اختياري)
def animated_text(text):
    result = pyfiglet.figlet_format(text, font="slant")
    return result

# دالة للحصول على تفاصيل الفيديو
def get_video_details(youtube_url):
    try:
        options = {'quiet': True, 'skip_download': True}
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
        return info
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# دالة للحصول على تفاصيل الصوت
def get_audio_details(info):
    try:
        audio_formats = [fmt for fmt in info['formats'] if fmt.get('vcodec') == 'none' and fmt['ext'] == 'm4a']
        if audio_formats:
            best_audio = max(audio_formats, key=lambda x: x.get('abr', 0))
            return best_audio['format_id']
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# دالة للحصول على صيغ الفيديو
def get_video_formats(info):
    try:
        video_formats = [fmt for fmt in info['formats'] if fmt['ext'] == 'mp4' and fmt.get('height')]
        unique_formats = {}
        for fmt in video_formats:
            height = fmt['height']
            if height not in unique_formats or fmt.get('tbr', 0) > unique_formats[height].get('tbr', 0):
                unique_formats[height] = fmt
        sorted_formats = sorted(unique_formats.values(), key=lambda x: x['height'])
        return sorted_formats
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# دالة لتحميل الملف
def download_file(youtube_url, format_id, title, extension, chat_id):
    try:
        output_folder = "downloads"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        options = {
            'format': format_id,
            'outtmpl': os.path.join(output_folder, f'{title}.{extension}'),
            'progress_hooks': [lambda d: progress_hook(d, chat_id)],
        }
        with YoutubeDL(options) as ydl:
            ydl.download([youtube_url])
        return os.path.join(output_folder, f'{title}.{extension}')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# دالة لتتبع التقدم
def progress_hook(d, chat_id):
    if d['status'] == 'downloading':
        percent = d['_percent_str']
        speed = d['_speed_str']
        eta = d['_eta_str']
        bot.send_message(chat_id, f"جاري التحميل... {percent} | السرعة: {speed} | الوقت المتبقي: {eta}")
    elif d['status'] == 'finished':
        bot.send_message(chat_id, "تم التحميل بنجاح! جاري الرفع...")

# بدء البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحبًا! أرسل لي رابط فيديو يوتيوب لتحميله.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "youtube.com" in url or "youtu.be" in url:
        info = get_video_details(url)
        if info:
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtn1 = types.KeyboardButton('تحميل الصوت (m4a)')
            itembtn2 = types.KeyboardButton('تحميل الفيديو (mp4)')
            markup.add(itembtn1, itembtn2)
            bot.send_message(message.chat.id, "اختر ما تريد تحميله:", reply_markup=markup)
            bot.register_next_step_handler(message, lambda m: handle_choice(m, info))
        else:
            bot.reply_to(message, "حدث خطأ أثناء معالجة الفيديو. يرجى التحقق من الرابط والمحاولة مرة أخرى.")
    else:
        bot.reply_to(message, "الرجاء إرسال رابط يوتيوب صحيح.")

def handle_choice(message, info):
    choice = message.text
    if choice == 'تحميل الصوت (m4a)':
        audio_format_id = get_audio_details(info)
        if audio_format_id:
            bot.send_message(message.chat.id, "جاري تحميل الصوت...")
            file_path = download_file(info['webpage_url'], audio_format_id, info['title'], 'm4a', message.chat.id)
            if file_path:
                with open(file_path, 'rb') as audio_file:
                    bot.send_audio(message.chat.id, audio_file)
                os.remove(file_path)
            else:
                bot.send_message(message.chat.id, "حدث خطأ أثناء التحميل.")
        else:
            bot.send_message(message.chat.id, "لا تتوفر صيغة صوتية.")
    elif choice == 'تحميل الفيديو (mp4)':
        video_formats = get_video_formats(info)
        if video_formats:
            markup = types.ReplyKeyboardMarkup(row_width=2)
            for i, fmt in enumerate(video_formats, 1):
                markup.add(types.KeyboardButton(f"{fmt['height']}p"))
            bot.send_message(message.chat.id, "اختر جودة الفيديو:", reply_markup=markup)
            bot.register_next_step_handler(message, lambda m: handle_video_quality(m, info, video_formats))
        else:
            bot.send_message(message.chat.id, "لا تتوفر صيغ فيديو.")
    else:
        bot.send_message(message.chat.id, "اختيار غير صحيح. الرجاء المحاولة مرة أخرى.")

def handle_video_quality(message, info, video_formats):
    selected_quality = message.text.replace('p', '')
    selected_format = next((fmt for fmt in video_formats if str(fmt['height']) == selected_quality), None)
    if selected_format:
        bot.send_message(message.chat.id, f"جاري تحميل الفيديو بجودة {selected_quality}p...")
        file_path = download_file(info['webpage_url'], selected_format['format_id'], info['title'], 'mp4', message.chat.id)
        if file_path:
            with open(file_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)
            os.remove(file_path)
        else:
            bot.send_message(message.chat.id, "حدث خطأ أثناء التحميل.")
    else:
        bot.send_message(message.chat.id, "جودة غير صالحة. الرجاء المحاولة مرة أخرى.")

# تشغيل البوت
bot.polling()
