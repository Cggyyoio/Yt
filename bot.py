import telebot
from yt_dlp import YoutubeDL
import os

# توكن البوت
bot = telebot.TeleBot("7165480067:AAGqlNq4-zHKOt4IAr1XaBt7Q4wBzgIQZHY")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً! ابعتلي رابط يوتيوب وهنزله لك.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    try:
        url = message.text
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)
        
        # إرسال الفيديو للمستخدم
        with open(file_name, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)
        
        # حذف الفيديو بعد الإرسال
        os.remove(file_name)
    
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {e}")

# تشغيل البوت
bot.polling()
