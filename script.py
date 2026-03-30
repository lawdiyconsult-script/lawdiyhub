import os, json, requests
import google.generativeai as genai

# ดึงค่าจาก GitHub Secrets
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
YT_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 1. ใส่ ID ของ Folder หลัก (Master Folder) ที่รวมทุกเรื่องไว้ตรงนี้
DRIVE_FOLDER_ID = "17L88mtW5Nl5Boh9-ETWwVyGHNiUzMnnh" 

def get_drive_folders():
    try:
        # ดึงรายชื่อ Folder ย่อยภายใต้ Master Folder
        url = f"https://www.googleapis.com/drive/v3/files?q='{DRIVE_FOLDER_ID}'+in+parents+and+mimeType='application/vnd.google-apps.folder'&fields=files(name,webViewLink)&key={YT_KEY}"
        res = requests.get(url).json()
        return res.get('files', [])
    except:
        return []

def main():
    # 2. ดึงวิดีโอจาก YouTube (Max 50 รายการ และกรอง Shorts ออก)
    yt_url = f"https://www.googleapis.com/youtube/v3/search?key={YT_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=50&type=video&videoDuration=medium"
    yt_res = requests.get(yt_url).json()
    yt_items = yt_res.get('items', [])
    
    # 3. ดึงรายชื่อ Folder จาก Drive มาเตรียมไว้
    drive_folders = get_drive_folders()
    
    all_data = []
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    for item in yt_items:
        v_id = item['id']['videoId']
        title = item['snippet']['title']
        desc = item['snippet']['description']
        thumb = item['snippet']['thumbnails']['high']['url']
        
        # --- Logic จับคู่ Folder ---
        download_link = ""
        for folder in drive_folders:
            # ถ้าชื่อ Folder (เช่น "มรดก") ปรากฏอยู่ในชื่อวิดีโอ ให้ส่งไปที่ Folder นั้น
            # เราใช้ .lower() เพื่อให้ค้นหาได้ไม่ว่าพิมพ์เล็กหรือใหญ่
            clean_folder_name = folder['name'].lower()
            if clean_folder_name in title.lower():
                download_link = folder['webViewLink']
                break
        
        # --- สรุปเนื้อหาด้วย AI ---
        try:
            prompt = f"สรุปเนื้อหากฎหมายจากชื่อวิดีโอ '{title}' และคำอธิบาย '{desc}' เป็นข้อสั้นๆ ไม่เกิน 3 บรรทัด"
            ai_res = model.generate_content(prompt)
            summary = ai_res.text
        except:
            summary = "คลิกเพื่อชมวิดีโอและดูรายละเอียดเพิ่มเติม"

        all_data.append({
            "title": title,
            "summary": summary,
            "videoUrl": f"https://www.youtube.com/watch?v={v_id}",
            "thumbnail": thumb,
            "downloadUrl": download_link
        })

    # บันทึกข้อมูลลง JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
