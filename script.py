import os, json, requests
import google.generativeai as genai

# ดึงค่าจาก Secrets
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
YT_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

def main():
    # 1. ดึงข้อมูลวิดีโอจาก YouTube (ดึง Snippet พื้นฐาน)
    url = f"https://www.googleapis.com/youtube/v3/search?key={YT_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=5&type=video"
    print(f"Fetching from YouTube Channel: {CHANNEL_ID}")
    
    response = requests.get(url).json()
    items = response.get('items', [])
    
    if not items:
        print("YouTube returned no videos. Please check API Key and Channel ID.")
        # ใส่ข้อมูล Dummy เพื่อให้หน้าเว็บไม่ขาว
        all_data = [{
            "title": "ระบบกำลังรอข้อมูลใหม่",
            "summary": f"ตรวจสอบช่อง {CHANNEL_ID} หรือ API Key อีกครั้ง (YouTube Error: {response.get('error', {}).get('message', 'None')})",
            "videoUrl": "#",
            "thumbnail": "https://via.placeholder.com/400x225?text=LawDIYHub"
        }]
    else:
        all_data = []
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        for item in items:
            v_id = item['id']['videoId']
            title = item['snippet']['title']
            desc = item['snippet']['description']
            thumb = item['snippet']['thumbnails']['high']['url']
            
            # สรุปจากชื่อและคำอธิบาย (รวดเร็วและชัวร์กว่าดึง Transcript)
            try:
                prompt = f"สรุปเนื้อหาสำคัญของวิดีโอกฎหมายชื่อ '{title}' จากคำอธิบายนี้: {desc} (สรุปเป็นข้อๆ สั้นๆ ภาษาไทย)"
                ai_res = model.generate_content(prompt)
                summary = ai_res.text
            except:
                summary = desc[:200] + "..." # ถ้า AI มีปัญหา ให้ใช้คำอธิบายย่อๆ แทน

            all_data.append({
                "title": title,
                "summary": summary,
                "videoUrl": f"https://www.youtube.com/watch?v={v_id}",
                "thumbnail": thumb
            })
            print(f"Added: {title}")

    # 2. บันทึกไฟล์
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("data.json updated successfully.")

if __name__ == "__main__":
    main()
