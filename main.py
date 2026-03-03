import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient

# Hardcoded Credentials (Kyunki repo private rahega)
API_ID = 33675350
API_HASH = "2f97c845b067a750c9f36fec497acf97"
BOT_TOKEN = "8792449250:AAE4Fr_C-vHZUcWP60M8Jyn_bMnxqc1fKAc"
MONGO_URL = "mongodb+srv://salonisingh6265_db_user:U50ONNZZFUbh0iQI@cluster0.41mb27f.mongodb.net/?appName=Cluster0"

# MongoDB Setup
print("Connecting to MongoDB...")
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client["InstaAudioBot"]
users_collection = db["users"]

app = Client("InstaAudioBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Save user to Database if not exists
    if not await users_collection.find_one({"user_id": user_id}):
        await users_collection.insert_one({"user_id": user_id, "username": message.from_user.username})
        print(f"New user saved to DB: {user_id}")

    welcome_text = (
        "🎧 **Wassup! Welcome to the Ultimate Insta Audio Bot.**\n\n"
        "Just drop any **Instagram Reel or Video Link** here, and I'll extract the absolute best quality (320kbps) MP3 for you. 🚀\n\n"
        "Let's get the vibe going! Drop a link 👇"
    )
    await message.reply_text(welcome_text)

@app.on_message(filters.text & (filters.regex(r"instagram\.com")))
async def download_audio(client: Client, message: Message):
    url = message.text
    status_msg = await message.reply_text("⚡️ **Vibe check! Fetching your audio...**")

    # Clean yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    file_path = None

    try:
        await status_msg.edit_text("🔥 **Extracting the highest quality MP3... Hold tight!**")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict).rsplit('.', 1)[0] + '.mp3'

        await status_msg.edit_text("🚀 **Uploading fresh audio directly to you...**")
        
        await message.reply_audio(
            audio=file_path,
            title=info_dict.get('title', 'Insta Vibe 🎵'),
            performer=info_dict.get('uploader', '@unknown'),
            caption="✨ **Extracted with ❤️ via your Bot**"
        )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ **Oops! Something broke:**\n`{str(e)}`")

    finally:
        # 500MB DISK SAVER: Always delete local file after upload
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧹 Trashed local file to save space: {file_path}")

print("🚀 Bot is up and running...")
app.run()
          
