import os
import json
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import requests

# ดึงค่าจาก GitHub Secrets ที่คุณตั้งไว้
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
YT_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# ตั้งค่า Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_latest_videos():
    # ดึงวิดีโอ 5 อันล่าสุดจากช่องที่ระบุ
    url = f"https://www.googleapis.com/youtube/v3/search?key={YT_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=5&type=video"
    res = requests.get(url).json()
    return res.get('items', [])

def main():
    videos = get_latest_videos()
    all_data = []
    
    for v in videos:
        v_id = v['id']['videoId']
        title = v['snippet']['title']
        thumb = v['snippet']['thumbnails']['high']['url']
        
        try:
            # 1. ดึง Transcript ภาษาไทย
            ts = YouTubeTranscriptApi.get_transcript(v_id, languages=['th'])
            full_text = " ".join([i['text'] for i in ts])
            
            # 2. ให้ AI สรุปเนื้อหากฎหมาย
            prompt = f"สรุปเนื้อหากฎหมายจากวิดีโอชื่อ '{title}' โดยใช้ข้อความนี้: {full_text} สรุปเป็นข้อๆ ให้คนทั่วไปเข้าใจง่าย"
            response = model.generate_content(prompt)
            summary = response.text
            
            all_data.append({
                "title": title,
                "summary": summary,
                "videoUrl": f"https://www.youtube.com/watch?v={v_id}",
                "thumbnail": thumb
            })
            print(f"Processed: {title}")
        except Exception as e:
            print(f"Skip {title}: {e}")

    # 3. บันทึกเป็นไฟล์ data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
