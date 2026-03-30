import os, json, requests

# ดึงค่าจาก GitHub Secrets
YT_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
DRIVE_FOLDER_ID = "17L88mtW5Nl5Boh9-ETWwVyGHNiUzMnnh" 

def get_drive_folders():
    try:
        # ดึงรายชื่อ Folder ย่อยภายใต้ Master Folder
        url = f"https://www.googleapis.com/drive/v3/files?q='{DRIVE_FOLDER_ID}'+in+parents+and+mimeType='application/vnd.google-apps.folder'&fields=files(name,webViewLink)&key={YT_KEY}"
        res = requests.get(url).json()
        return res.get('files', [])
    except: return []

def main():
    drive_folders = get_drive_folders()
    all_yt_items = []
    next_page_token = None

    # ลูปดึงวิดีโอจนครบ (182 คลิป)
    while True:
        yt_url = f"https://www.googleapis.com/youtube/v3/search?key={YT_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=50&type=video&videoDuration=medium"
        if next_page_token:
            yt_url += f"&pageToken={next_page_token}"
        
        res = requests.get(yt_url).json()
        items = res.get('items', [])
        all_yt_items.extend(items)
        
        next_page_token = res.get('nextPageToken')
        if not next_page_token or len(all_yt_items) >= 200: # จำกัดไว้ที่ไม่เกิน 200 เพื่อความปลอดภัย
            break

    all_data = []
    for item in all_yt_items:
        v_id = item['id']['videoId']
        title = item['snippet']['title']
        desc = item['snippet']['description']
        thumb = item['snippet']['thumbnails']['high']['url']
        
        # จับคู่ Folder Drive
        download_link = ""
        for folder in drive_folders:
            # ใช้คำสำคัญจากชื่อโฟลเดอร์มาเช็ค
            folder_keyword = folder['name'].replace("เอกสาร", "").replace("คดี", "").strip().lower()
            if folder_keyword and folder_keyword in title.lower():
                download_link = folder['webViewLink']
                break

        all_data.append({
            "title": title,
            "summary": desc[:150] + "...", # ใช้คำอธิบายจาก YouTube แทนการรอ AI เพื่อความเร็ว
            "videoUrl": f"https://www.youtube.com/watch?v={v_id}",
            "thumbnail": thumb,
            "downloadUrl": download_link
        })

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
