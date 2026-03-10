import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from pytube import YouTube

# Your Bot Token
TOKEN = '8760715026:AAExNkaxzVAtaAskkIMgZvEju6yGsYNSL8I'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Keep Alive Server for Render ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def run_health_check(): 
    try:
        server = HTTPServer(('0.0.0.0', 10000), HealthCheck)
        server.serve_forever()
    except:
        pass

threading.Thread(target=run_health_check, daemon=True).start()
# ------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a YouTube link to download the music.")

async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        status_msg = await update.message.reply_text("Processing... Please wait.")
        try:
            yt = YouTube(url)
            audio = yt.streams.filter(only_audio=True).first()
            downloaded_file = audio.download(output_path=".")
            
            # Rename to mp3
            base, ext = os.path.splitext(downloaded_file)
            new_file = base + '.mp3'
            os.rename(downloaded_file, new_file)

            # Send audio
            await update.message.reply_audio(audio=open(new_file, 'rb'), caption=yt.title)
            await status_msg.delete()
            
            # Cleanup
            os.remove(new_file) 
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")
    else:
        await update.message.reply_text("Please send a valid YouTube link.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_music))
    application.run_polling()
    