import os
import requests
import subprocess
import asyncio
import aiohttp
import aiofiles
from urllib.parse import urlparse, unquote
import re

# Simple logger if logger.py fails
try:
    from logger import logger
except:
    import logging
    logger = logging.getLogger(__name__)

class SarvamDownloader:
    """Handler for Sarvam Career Institute videos"""
    
    @staticmethod
    def is_sarvam_url(url):
        """Check if URL is from Sarvam Career Institute"""
        return "sarvamcareerinstitute.in/serve_videouweb.php" in url
    
    @staticmethod
    async def download_video(url, output_path, progress_callback=None):
        """Download video from Sarvam Career Institute"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'video/mp4,video/*;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://sarvamcareerinstitute.in/',
                'Origin': 'https://sarvamcareerinstitute.in',
            }
            
            print(f"Downloading from: {url}")
            
            # Method 1: Using requests (simpler for Heroku)
            try:
                response = requests.get(url, headers=headers, stream=True, verify=False, timeout=30)
                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    
                    with open(output_path, 'wb') as file:
                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                                downloaded += len(chunk)
                                
                                if progress_callback and total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    print(f"Progress: {progress:.1f}%", end='\r')
                    
                    print(f"\nDownload complete: {output_path}")
                    return output_path
            except Exception as e:
                print(f"Requests method failed: {e}")
            
            # Method 2: Fallback to wget
            try:
                cmd = f'wget "{url}" -O "{output_path}" --no-check-certificate --header="User-Agent: Mozilla/5.0"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    print(f"Download complete with wget: {output_path}")
                    return output_path
            except Exception as e:
                print(f"Wget method failed: {e}")
        
        except Exception as e:
            print(f"Download error: {e}")
        
        return None

class VideoHelper:
    """General video helper functions"""
    
    @staticmethod
    def get_video_duration(file_path):
        """Get video duration using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'error', '-show_entries',
                'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip())
        except:
            return 0
    
    @staticmethod
    def generate_thumbnail(video_path, output_path=None):
        """Generate thumbnail from video"""
        try:
            if not output_path:
                output_path = video_path.replace('.mp4', '_thumb.jpg')
            
            duration = VideoHelper.get_video_duration(video_path)
            timestamp = min(duration / 2, 1) if duration > 0 else 1
            
            cmd = [
                'ffmpeg', '-ss', str(timestamp), '-i', video_path,
                '-vframes', '1', '-q:v', '2', output_path, '-y'
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if os.path.exists(output_path):
                return output_path
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")
        return None

class FileParser:
    """Parse text files with video links"""
    
    @staticmethod
    def parse_txt_file(file_path):
        """Parse text file and extract links"""
        links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Try to find URL in the line
                    url_match = re.search(r'https?://[^\s]+', line)
                    if url_match:
                        url = url_match.group()
                        # Extract name (everything before the URL)
                        name = line[:url_match.start()].strip().rstrip(':').strip()
                        if not name:
                            name = f"Video_{len(links) + 1}"
                        
                        links.append({
                            'name': name,
                            'url': url
                        })
        except Exception as e:
            print(f"Error parsing file: {e}")
        
        return links
