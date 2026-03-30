import os, json, requests

# ดึงค่าจาก GitHub Secrets
YT_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
# ใช้ Folder ID ที่คุณแจ้งมา
DRIVE_FOLDER_ID = "17L88mtW5Nl5Boh9-ETWwVyGHNiUzMnnh" 

def get_drive_folders():
    try:
        # ดึงรายชื่อโฟลเดอร์ย่อย (เรื่องต่างๆ) ภายใต้ Master Folder
        url = f"https://www.googleapis.com/drive/v3/files?q='{DRIVE_FOLDER_ID}'+in+parents+and+mimeType='application/vnd.google-apps.folder'&fields=files(name,webViewLink)&key={YT_KEY}"
        res = requests.get(url).json()
        return res.get('files', [])
    except Exception as e:
        print(f"Drive Error: {e}")
        return []

def main():
    # 1. เตรียมข้อมูลจาก Drive
    drive_folders = get_drive_folders()
    print(f"พบโฟลเดอร์ใน Drive ทั้งหมด {len(drive_folders)} โฟลเดอร์")

    # 2. ดึงวิดีโอจาก YouTube จนครบทั้งหมด (รองรับ 182 คลิป)
    all_yt_items = []
    next_page_token = None

    while True:
        yt_url = f"https://www.googleapis.com/youtube/v3/search?key={YT_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=50&type=video&videoDuration=medium"
        if next_page_token:
            yt_url += f"&pageToken={next_page_token}"
        
        res = requests.get(yt_url).json()
        items = res.get('items', [])
        all_yt_items.extend(items)
        
        next_page_token = res.get('nextPageToken')
        # หยุดเมื่อไม่มีหน้าถัดไป หรือได้คลิปพอสมควร (ตั้งเผื่อไว้ที่ 250)
        if not next_page_token or len(all_yt_items) >= 250:
            break

    print(f"ดึงวิดีโอจาก YouTube สำเร็จ {len(all_yt_items)} คลิป")

    # 3. ประมวลผลและจับคู่ข้อมูล (ปรับปรุงใหม่ให้ใจกว้างขึ้น)
    # 3. ประมวลผลและจับคู่ข้อมูล (ปรับปรุงใหม่ให้ใจกว้างขึ้น)
    all_data = []
    for item in all_yt_items:
        v_id = item['id']['videoId']
        title = item['snippet']['title']
        desc = item['snippet']['description']
        thumb = item['snippet']['thumbnails']['high']['url']
        
        download_link = ""
        title_clean = title.lower().replace(" ", "") # ลบช่องว่างออกเพื่อให้เทียบง่ายขึ้น

        for folder in drive_folders:
            folder_full_name = folder['name'].lower()
            # ตัดคำขยะออกให้เหลือแต่ Keyword หลักจริงๆ
            keyword = folder_full_name.replace("เอกสาร", "").replace("คดี", "").replace("เรื่อง", "").replace("-", "").strip()
            
            # --- Logic ใหม่: ตรวจสอบแบบไขว้ (Cross-check) ---
            # 1. ถ้าคำสำคัญอยู่ในชื่อคลิป
            # 2. หรือถ้าชื่อคลิป (บางส่วน) อยู่ในชื่อโฟลเดอร์
            if len(keyword) > 1 and (keyword in title_clean or title_clean in folder_full_name.replace(" ", "")):
                download_link = folder['webViewLink']
                break
        
        # --- Logic เสริม: ดักคำยอดฮิต (Manual Fallback) ---
        if not download_link:
            if "มรดก" in title: 
                # หาโฟลเดอร์ที่มีคำว่ามรดก
                for f in drive_folders:
                    if "มรดก" in f['name']: download_link = f['webViewLink']; break

        all_data.append({
            "title": title,
            "summary": desc[:120] + "...", 
            "videoUrl": f"https://www.youtube.com/watch?v={v_id}",
            "thumbnail": thumb,
            "downloadUrl": download_link
        })

    # 4. บันทึกไฟล์ data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("บันทึกข้อมูลลง data.json เรียบร้อยแล้ว")

if __name__ == "__main__":
    main()
