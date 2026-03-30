import os, json, requests

# ดึงค่าจาก GitHub Secrets
YT_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
DRIVE_FOLDER_ID = "17L88mtW5Nl5Boh9-ETWwVyGHNiUzMnnh" 

def get_drive_folders():
    try:
        url = f"https://www.googleapis.com/drive/v3/files?q='{DRIVE_FOLDER_ID}'+in+parents+and+mimeType='application/vnd.google-apps.folder'&fields=files(name,webViewLink)&key={YT_KEY}"
        res = requests.get(url).json()
        return res.get('files', [])
    except: return []

def main():
    drive_folders = get_drive_folders()
    print(f"เชื่อมต่อ Drive สำเร็จ: พบ {len(drive_folders)} หัวข้อ")

    all_yt_items = []
    next_page_token = None

    while True:
        yt_url = f"https://www.googleapis.com/youtube/v3/search?key={YT_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=50&type=video&videoDuration=medium"
        if next_page_token: yt_url += f"&pageToken={next_page_token}"
        
        res = requests.get(yt_url).json()
        items = res.get('items', [])
        all_yt_items.extend(items)
        
        next_page_token = res.get('nextPageToken')
        if not next_page_token or len(all_yt_items) >= 200: break

    all_data = []
    for item in all_yt_items:
        v_id = item['id']['videoId']
        title = item['snippet']['title']
        desc = item['snippet']['description']
        thumb = item['snippet']['thumbnails']['high']['url']
        
        download_link = ""
        # --- Logic การจับคู่แบบยืดหยุ่นพิเศษ ---
        for folder in drive_folders:
            f_name = folder['name'].lower()
            # ตัดคำว่า 'เอกสาร', 'คำฟ้อง', 'คำร้อง', 'สอนทำ' ออกเพื่อหา Keyword จริงๆ
            core_keyword = f_name.replace("เอกสาร", "").replace("คำฟ้อง", "").replace("คำร้อง", "").replace("คดี", "").replace("สอนทำ", "").strip()
            
            # ถ้า Keyword หลัก (เช่น 'มรดก') อยู่ในชื่อวิดีโอ ให้จับคู่ทันที
            if len(core_keyword) >= 2 and core_keyword in title.lower():
                download_link = folder['webViewLink']
                break
            
            # ดักเคสพิเศษที่คุณตั้งชื่อโฟลเดอร์ยาวๆ
            if "มรดก" in f_name and "มรดก" in title:
                download_link = folder['webViewLink']
                break
        
        all_data.append({
            "title": title,
            "summary": desc[:120] + "...", 
            "videoUrl": f"https://www.youtube.com/watch?v={v_id}",
            "thumbnail": thumb,
            "downloadUrl": download_link
        })

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print(f"บันทึกข้อมูลเรียบร้อย! รวม {len(all_data)} รายการ")

if __name__ == "__main__":
    main()
