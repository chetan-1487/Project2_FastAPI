from fastapi import FastAPI, HTTPException, Form  # Import FastAPI and necessary modules
from fastapi.responses import FileResponse  # Import FileResponse to send files as responses
import os  # Import os module for file handling
import yt_dlp  # Import yt_dlp for YouTube downloading

app = FastAPI()  # Create a FastAPI app instance

OUTPUT_DIR = os.getcwd()  # Set output directory to the current working directory

# Function to download and convert YouTube video to MP3
def download_and_convert(url: str) -> str:
    try:
        output_path = os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s")  # Set output filename format

        ydl_opts = {
            'format': 'bestaudio/best',  # Download best audio quality
            'outtmpl': output_path,  # Output file template
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # Use FFmpeg to extract audio
                'preferredcodec': 'mp3',  # Convert to MP3 format
                'preferredquality': '192',  # Set audio quality to 192 kbps
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)  # Extract and download video info
            downloaded_file = ydl.prepare_filename(info)  # Get downloaded filename
            mp3_file = downloaded_file.rsplit('.', 1)[0] + '.mp3'  # Change extension to .mp3

            if os.path.exists(mp3_file):  # Check if MP3 file exists
                return mp3_file
            else:
                raise HTTPException(status_code=500, detail="Conversion failed.")  # Raise error if conversion failed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")  # Handle errors

# API endpoint to convert YouTube video to MP3
@app.post("/convert-audio/")
async def convert_audio(url: str = Form(...)):  # Accept YouTube URL as form data
    mp3_file = download_and_convert(url)  # Call function to download and convert video
    return FileResponse(mp3_file, media_type="audio/mpeg", filename=os.path.basename(mp3_file))  # Return MP3 file as response
