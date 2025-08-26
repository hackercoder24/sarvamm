import os
import sys
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from config import *
from helper import SarvamDownloader, VideoHelper, FileParser
import time

# Try to import progress bar, use simple version if fails
try:
    from p_bar import progress_bar
except:
    async def progress_bar(current, total, text, message, start_time):
        pass

# Initialize bot
app = Client(
    "sarvam_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="/tmp"
)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Start command handler"""
    await message.reply_text(
        "**🎬 Sarvam Video Downloader Bot**\n\n"
        "Commands:\n"
        "• `/txt` - Upload a text file with video links\n"
        "• `/ping` - Check if bot is alive\n\n"
        f"User: {message.from_user.mention}"
    )

@app.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    """Ping command to check if bot is alive"""
    await message.reply_text("🏓 Pong! Bot is alive.")

@app.on_message(filters.command("txt"))
async def txt_handler(client: Client, message: Message):
    """Handle text file with video links"""
    
    # Check if user is authorized
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ You are not authorized to use this command.")
        return
    
    msg = await message.reply_text("**📁 Send me the text file containing video links:**")
    
    try:
        # Wait for file
        file_msg: Message = await client.listen(message.chat.id, timeout=60)
        
        if not file_msg.document:
            await msg.edit("❌ **Please send a valid text file!**")
            return
        
        # Download file
        await msg.edit("📥 **Downloading file...**")
        file_path = await file_msg.download()
        
        # Parse links
        links = FileParser.parse_txt_file(file_path)
        
        if not links:
            await msg.edit("❌ **No valid links found in the file!**")
            os.remove(file_path)
            return
        
        await msg.edit(f"**✅ Found {len(links)} links**\n\nStarting downloads...")
        
        # Clean up
        os.remove(file_path)
        
        # Process downloads
        success_count = 0
        failed_count = 0
        
        for idx, link_data in enumerate(links, 1):
            name = link_data['name']
            url = link_data['url']
            
            status_msg = await message.reply_text(
                f"**📥 Downloading {idx}/{len(links)}**\n"
                f"Name: {name[:50]}..."
            )
            
            try:
                # Check if it's a Sarvam URL
                if SarvamDownloader.is_sarvam_url(url):
                    # Download video
                    output_file = f"/tmp/{idx}_{name[:30]}.mp4"
                    
                    video_path = await SarvamDownloader.download_video(url, output_file)
                    
                    if video_path and os.path.exists(video_path):
                        # Generate thumbnail
                        thumb_path = VideoHelper.generate_thumbnail(video_path)
                        
                        # Get video duration
                        duration = int(VideoHelper.get_video_duration(video_path))
                        
                        # Upload to Telegram
                        await status_msg.edit("📤 **Uploading...**")
                        
                        caption = f"**📹 {name}**\n\nVideo: {idx}/{len(links)}"
                        
                        await message.reply_video(
                            video=video_path,
                            caption=caption,
                            duration=duration,
                            thumb=thumb_path if thumb_path else None,
                            supports_streaming=True
                        )
                        
                        success_count += 1
                        await status_msg.delete()
                        
                        # Clean up files
                        os.remove(video_path)
                        if thumb_path and os.path.exists(thumb_path):
                            os.remove(thumb_path)
                    else:
                        failed_count += 1
                        await status_msg.edit(f"❌ **Failed to download:** {name[:50]}")
                else:
                    await status_msg.edit(f"⚠️ **Unsupported URL:** {name[:50]}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"Error processing {name}: {e}")
                failed_count += 1
                await status_msg.edit(f"❌ **Error:** {str(e)[:100]}")
            
            # Small delay
            await asyncio.sleep(2)
        
        # Final status
        await msg.edit(
            f"**✅ Complete!**\n\n"
            f"Success: {success_count}\n"
            f"Failed: {failed_count}"
        )
        
    except asyncio.TimeoutError:
        await msg.edit("⏰ **Timeout! Please try again.**")
    except Exception as e:
        print(f"Error in txt_handler: {e}")
        await msg.edit(f"❌ **Error:** {str(e)[:200]}")

# Main
if __name__ == "__main__":
    print("Starting bot...")
    app.run()
