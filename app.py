import os
import requests
import subprocess
import json
import random
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables from .env file
load_dotenv()

# --- Initialize Flask App ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- API Keys and Configuration ---
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Configure the Gemini API client
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

PEXELS_VIDEO_API_URL = "https://api.pexels.com/videos/search"
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"

# --- Optimized HTTP Session with Retries ---
def create_session():
    """Create a requests session with timeout and retry configuration"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session

# --- Function to get audio duration ---
def get_audio_duration(audio_path):
    """Get the duration of an audio file in seconds"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
    except Exception as e:
        print(f"Error getting audio duration: {e}")
    return 60.0  # Default to 60 seconds if can't determine

# --- Intelligent function to select a reasonably sized video URL ---
def get_best_video_url(video_files):
    """Prioritizes smaller video files for faster downloads and processing."""
    if not video_files:
        return None
    
    # Sort by width, but prioritize smaller files overall
    sorted_videos = sorted(video_files, key=lambda x: x.get('file_size', 999999999) or 999999999)
    
    # Try to find a good quality (HD) but reasonably sized file first
    for video in sorted_videos:
        width = video.get('width', 0)
        file_size = video.get('file_size') or 0
        if width == 1920 and file_size < 50 * 1024 * 1024: # Prefer 1080p under 50MB
             print(f"  -> Found optimal clip: 1080p, {file_size/1024/1024:.1f}MB")
             return video.get('link')

    # If not, take the smallest file available that is still decent quality
    for video in sorted_videos:
        width = video.get('width', 0)
        if width >= 1280:
            print(f"  -> Using fallback clip: {width}p")
            return video.get('link')
            
    # If all else fails, return the first one
    return sorted_videos[0].get('link') if sorted_videos else None

# --- Enhanced AI Content Generation Function ---
def generate_ai_video_content(niche):
    if not GEMINI_API_KEY:
        print("❌ Gemini API key missing.")
        return None

    print(f"🧠 Generating AI content for 1-2 minute video: {niche}")
    
    # Enhanced prompts for longer content (1-2 minutes)
    if niche == "horror stories":
        prompt_segment = "Create a terrifying horror story that is exactly 300-400 words long (suitable for 1-2 minutes of narration). Use vivid, spine-chilling descriptions and build suspense throughout. The story must be engaging and suitable for a short video. Also, provide a list of 8 specific, visually descriptive keywords for searching stock videos (e.g., 'dark forest path', 'creaking door', 'shadowy figure', 'abandoned house', 'flickering candle', 'storm clouds', 'empty corridor', 'mysterious fog')."
    elif niche == "childrens cartoon comedy":
        prompt_segment = "Write a funny, light-hearted comedy script for children that is exactly 300-400 words long (suitable for 1-2 minutes of narration). The story should feature talking animals and multiple silly situations with a clear beginning, middle, and end. Also, provide a list of 8 fun, simple keywords for searching animated or cartoon-style videos (e.g., 'happy squirrel', 'bouncing ball', 'silly dance', 'colorful playground', 'laughing children', 'cute animals', 'rainbow', 'birthday party')."
    elif niche == "motivational":
        prompt_segment = "Write a powerful and inspiring motivational speech that is exactly 300-400 words long (suitable for 1-2 minutes of narration). Focus on overcoming challenges, achieving goals, and personal growth. Use strong, encouraging language with specific examples. Also, provide a list of 8 symbolic keywords for searching stock videos (e.g., 'mountain sunrise', 'person crossing finish line', 'eagle soaring', 'ocean waves', 'city skyline', 'runner training', 'success celebration', 'teamwork')."
    elif niche == "historical facts":
        prompt_segment = "Generate a 'Top 8 Interesting Facts' script about a randomly chosen famous person from history that is exactly 300-400 words long (suitable for 1-2 minutes of narration). Make the facts surprising, engaging, and historically accurate. Also, provide a list of 8 keywords related to the facts for searching stock videos (e.g., 'ancient manuscripts', 'historical artifacts', 'old paintings', 'castle architecture', 'vintage photographs', 'library books', 'museum exhibits', 'historical timeline')."
    else:
        return None

    full_prompt = f"""
    {prompt_segment}
    
    IMPORTANT: The script must be between 300-400 words to ensure 1-2 minutes of narration time.
    
    Return your response ONLY as a single, valid JSON object with three keys:
    1. "title": A short, catchy title for the video.
    2. "script": The full text of the story/script (300-400 words).
    3. "visual_keywords": A JSON list of exactly 8 strings, representing diverse search terms for video clips.
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content(full_prompt)
        print("📥 Raw Gemini response received.")
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        content = json.loads(cleaned_response)
        
        # Validate script length
        script_words = len(content.get("script", "").split())
        print(f"Generated script has {script_words} words")
        
        if niche in ["horror stories"]: content["music_mood"] = "suspenseful"
        elif niche in ["childrens cartoon comedy"]: content["music_mood"] = "upbeat"
        else: content["music_mood"] = "inspirational"
        
        print("✅ AI-generated content package created")
        return content
    except Exception as e:
        print(f"🔥 Error generating AI content: {e}")
        return None

# --- Main Route ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Enhanced Video Generation Route ---
@app.route('/generate-videos', methods=['POST'])
def generate_videos_route():
    data = request.get_json()
    niche = data.get('niche')

    if not niche:
        return jsonify({"error": "A niche must be selected."}), 400

    print(f"--- Generating 1-2 Minute Video for niche: {niche} ---")
    
    content_package = generate_ai_video_content(niche)
    if not content_package:
        return jsonify({"error": "The AI failed to generate a valid content package."}), 500
    
    title = content_package.get("title", "AI Generated Video")
    script = content_package.get("script", "")
    visual_keywords = content_package.get("visual_keywords", [])
    music_mood = content_package.get("music_mood", "inspirational")

    output_dir = os.path.join('static', 'output')
    os.makedirs(output_dir, exist_ok=True)
    session = create_session()

    try:
        # 1. Generate Full-Length Narration Audio
        print("🔊 Generating full-length narration audio...")
        audio_filename = os.path.join(output_dir, "narration.mp3")
        
        # Check if ElevenLabs API key is available
        if not ELEVENLABS_API_KEY:
            return jsonify({"error": "ElevenLabs API key is missing. Please add ELEVENLABS_API_KEY to your .env file."}), 500
        
        # Enhanced TTS settings for longer, clearer audio
        tts_headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY}
        tts_data = {
            "text": script, 
            "model_id": "eleven_multilingual_v2", 
            "voice_settings": {
                "stability": 0.6, 
                "similarity_boost": 0.75,
                "style": 0.4,
                "use_speaker_boost": True
            }
        }
        
        try:
            tts_response = session.post(ELEVENLABS_API_URL, headers=tts_headers, json=tts_data, timeout=120)
            if tts_response.status_code == 401:
                return jsonify({"error": "Invalid ElevenLabs API key. Please check your API key in the .env file."}), 500
            tts_response.raise_for_status()
            
            with open(audio_filename, 'wb') as f: 
                f.write(tts_response.content)
            print("✅ Full-length narration audio saved.")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ ElevenLabs API error: {e}")
            return jsonify({"error": f"ElevenLabs API error: {str(e)}"}), 500

        # Get audio duration to match video length
        audio_duration = get_audio_duration(audio_filename)
        print(f"📏 Audio duration: {audio_duration:.2f} seconds")

        # 2. Download Multiple Diverse Video Clips
        print("🎬 Downloading multiple diverse video clips...")
        all_clip_paths = []
        
        # Download 2-3 clips per keyword for variety
        for i, keyword in enumerate(visual_keywords):
            print(f"  Searching for: {keyword}")
            # Remove 'gameplay' to get more relevant content
            search_query = keyword
            params = {"query": search_query, "per_page": 10, "orientation": "landscape"}
            pexels_headers = {"Authorization": PEXELS_API_KEY}
            
            try:
                video_response = session.get(PEXELS_VIDEO_API_URL, headers=pexels_headers, params=params, timeout=20)
                
                if video_response.status_code == 200:
                    videos = video_response.json().get('videos', [])
                    
                    # Download up to 2 clips per keyword
                    clips_downloaded = 0
                    for j, video in enumerate(videos[:3]):  # Try up to 3 videos
                        if clips_downloaded >= 2:  # Max 2 clips per keyword
                            break
                            
                        video_url = get_best_video_url(video['video_files'])
                        if video_url:
                            clip_path = os.path.join(output_dir, f"clip_{i}_{j}.mp4")
                            try:
                                with session.get(video_url, stream=True, timeout=45) as r:
                                    r.raise_for_status()
                                    with open(clip_path, 'wb') as f:
                                        for chunk in r.iter_content(chunk_size=8192): 
                                            f.write(chunk)
                                all_clip_paths.append(clip_path)
                                clips_downloaded += 1
                                print(f"    -> Downloaded clip {clips_downloaded} for '{keyword}'")
                            except Exception as e:
                                print(f"    -> Failed to download clip for '{keyword}': {e}")
                                continue
                    
                    if clips_downloaded == 0:
                        print(f"    -> No clips downloaded for '{keyword}'")
                else:
                    print(f"    -> No Pexels results for '{keyword}' (Status: {video_response.status_code})")
                    
            except Exception as e:
                print(f"    -> Error searching for '{keyword}': {e}")
                continue

        if not all_clip_paths:
            return jsonify({"error": "Could not find enough relevant video clips. Please try a different niche."}), 500

        print(f"✅ Downloaded {len(all_clip_paths)} video clips total")

        # 3. Create Video Sequence That Matches Audio Duration
        print("⚙️ Creating video sequence to match audio duration...")
        
        # Calculate clip duration to match total audio length
        clips_needed = len(all_clip_paths)
        clip_duration = max(3.0, audio_duration / clips_needed)  # At least 3 seconds per clip
        
        # Create concat file with proper durations
        concat_file_path = os.path.join(output_dir, "concat.txt")
        with open(concat_file_path, "w") as f:
            total_duration = 0
            clip_index = 0
            
            # Distribute clips across the audio duration
            while total_duration < audio_duration and clip_index < len(all_clip_paths) * 3:  # Allow cycling through clips
                current_clip = all_clip_paths[clip_index % len(all_clip_paths)]
                remaining_time = audio_duration - total_duration
                current_clip_duration = min(clip_duration, remaining_time)
                
                f.write(f"file '{os.path.basename(current_clip)}'\n")
                f.write(f"duration {current_clip_duration:.2f}\n")
                
                total_duration += current_clip_duration
                clip_index += 1
            
            # Add final clip without duration to ensure smooth ending
            if all_clip_paths:
                f.write(f"file '{os.path.basename(all_clip_paths[-1])}'\n")

        # 4. Assemble Final Video with FFmpeg
        print("⚙️ Assembling final video with FFmpeg...")
        final_video_path = os.path.join(output_dir, "final_video.mp4")
        music_file_path = os.path.join("music", f"{music_mood}.mp3")
        
        if os.path.exists(music_file_path):
            print(f"🎵 Using background music: {music_file_path}")
            # Enhanced command WITH music
            ffmpeg_command = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', 
                '-i', 'narration.mp3', '-i', os.path.join('../../', music_file_path),
                '-filter_complex', 
                '[0:v]scale=1280:720,setsar=1,fps=30[v];'
                '[2:a]volume=0.2[a_music];'
                '[1:a][a_music]amix=inputs=2:duration=first[a_out]',
                '-map', '[v]', '-map', '[a_out]',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', 
                '-c:a', 'aac', '-b:a', '128k',
                '-t', str(audio_duration),  # Match video length to audio
                '-y', os.path.basename(final_video_path)
            ]
        else:
            print(f"⚠️ Music file not found. Creating video without background music.")
            # Enhanced command WITHOUT music
            ffmpeg_command = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', 
                '-i', 'narration.mp3',
                '-map', '0:v', '-map', '1:a',
                '-vf', 'scale=1280:720,setsar=1,fps=30',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', 
                '-c:a', 'aac', '-b:a', '128k',
                '-t', str(audio_duration),  # Match video length to audio
                '-y', os.path.basename(final_video_path)
            ]

        # Execute FFmpeg command
        result = subprocess.run(ffmpeg_command, cwd=output_dir, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ FFmpeg error:", result.stderr)
            return jsonify({"error": f"Failed to assemble the video: {result.stderr}"}), 500
        
        print(f"✅✅✅ Video '{title}' created successfully! Duration: {audio_duration:.1f} seconds ✅✅✅")
        
        # Clean up individual clip files to save space
        for clip_path in all_clip_paths:
            try:
                os.remove(clip_path)
            except:
                pass
        
        return jsonify({
            "videos": [{
                "title": title,
                "url": f"/{final_video_path}",
                "duration": f"{audio_duration:.1f}s"
            }]
        })

    except Exception as e:
        print(f"🔥🔥🔥 An unexpected and critical error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)