import os
from pytube import YouTube
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# استبدل 'YOUR_BOT_TOKEN' بالـ API Token الذي حصلت عليه من BotFather
TOKEN ='7165480067:AAGqlNq4-zHKOt4IAr1XaBt7Q4wBzgIQZHY'

# مجلد التحميلات
DOWNLOAD_FOLDER = './downloads'

# تأكد من وجود مجلد التحميلات
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# دالة لتحميل الفيديو
def download_video(url, download_folder):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    file_path = stream.download(output_path=download_folder)
    return file_path

# دالة لتحميل الصوت
def download_audio(url, download_folder):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    file_path = stream.download(output_path=download_folder)
    base, _ = os.path.splitext(file_path)
    new_file = base + '.mp3'
    os.rename(file_path, new_file)
    return new_file

# دالة لمعالجة الأمر /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text('مرحبًا! أرسل لي رابط فيديو يوتيوب وسأحمل لك الفيديو أو الصوت.')

# دالة لمعالجة الرسائل النصية
def handle_message(update: Update, context: CallbackContext):
    url = update.message.text
    try:
        # تحميل الفيديو
        video_path = download_video(url, DOWNLOAD_FOLDER)
        update.message.reply_text('تم تحميل الفيديو! جارٍ الإرسال...')
        with open(video_path, 'rb') as video_file:
            update.message.reply_video(video_file)

        # تحميل الصوت
        audio_path = download_audio(url, DOWNLOAD_FOLDER)
        update.message.reply_text('تم تحميل الصوت! جارٍ الإرسال...')
        with open(audio_path, 'rb') as audio_file:
            update.message.reply_audio(audio_file)

    except Exception as e:
        update.message.reply_text(f'حدث خطأ: {e}')

# بدء البوت
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # إضافة معالجات الأوامر والرسائل
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # بدء الاستماع للرسائل
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
