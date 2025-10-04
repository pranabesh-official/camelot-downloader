#!/usr/bin/env python3

import yt_dlp
import os
import tempfile

def test_ytdlp_download():
    """Test if yt-dlp can download a simple video"""
    
    # Test URL - a short, simple video
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - should always be available
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "test_download")
    
    print(f"🧪 Testing yt-dlp download...")
    print(f"📁 Output path: {output_path}")
    print(f"🔗 URL: {test_url}")
    
    # Updated yt-dlp options for current YouTube restrictions
    ydl_opts = {
        'format': 'bestaudio[acodec!=none]/best[acodec!=none]/bestaudio/best',
        'outtmpl': output_path + '.%(ext)s',
        'noplaylist': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'audioquality': '192',  # Lower quality for test
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'no_warnings': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage'],
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("📥 Starting download...")
            ydl.download([test_url])
            
        # Check if file was created
        files = os.listdir(temp_dir)
        print(f"📁 Files created: {files}")
        
        if files:
            print("✅ yt-dlp download test PASSED")
            return True
        else:
            print("❌ yt-dlp download test FAILED - no files created")
            return False
            
    except Exception as e:
        print(f"❌ yt-dlp download test FAILED: {str(e)}")
        return False
    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass

if __name__ == "__main__":
    test_ytdlp_download()