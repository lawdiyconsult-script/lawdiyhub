import os, json, requests

YT_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
DRIVE_FOLDER_ID = "17L88mtW5Nl5Boh9-ETWwVyGHNiUzMnnh" 

def get_yt_data(duration_filter):
    all_items = []
    next_page_token = None
    try:
        while True:
            url = f"https://www.googleapis.com/youtube/v3/search?key={YT_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=50&type=video&videoDuration={duration_filter}"
            if next_page_token: url += f"&pageToken={next_page_token}"
            res = requests.get(url).json()
            items = res.get('items', [])
            all_items.extend(items)
            next_page_token = res.get('nextPageToken')
            if not next_page_token or len(all_items) >= 200: break
        return all_items
    except:
        return []

def main():
    # 1. ดึงวิดีโอยาว (เก็บใส่ตัวแปร long_vids)
    long_vids = get_yt_data("medium")
    # 2. ดึง Shorts (เก็บใส่ตัวแปร short_vids)
    short_vids = get_yt_data("short")
    
    # 3. ดึง Drive (Folders + Word + PDF)
    q = f"'{DRIVE_FOLDER_ID}' in parents and (mimeType = 'application/vnd.google-apps.folder' or mimeType = 'application/msword' or mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or mimeType = 'application/pdf')"
    drive_url = f"https://www.googleapis.com/drive/v3/files?q={q}&fields=files(name,webViewLink,mimeType)&key={YT_KEY}"
    
    try:
        drive_res = requests.get(drive_url).json()
        drive_items = drive_res.get('files', [])
    except:
        drive_items = []

    # จัดโครงสร้าง JSON (ใช้ชื่อตัวแปรให้ตรงกับข้างบน)
    output = {
        "long_videos": [{
            "title": i['snippet']['title'],
            "videoUrl": f"https://www.youtube.com/watch?v={i['id']['videoId']}",
            "thumbnail": i['snippet']['thumbnails']['high']['url']
        } for i in long_vids], # แก้จาก all_long_videos เป็น long_vids
        "shorts": [{
            "title": i['snippet']['title'],
            "videoUrl": f"https://www.youtube.com/watch?v={i['id']['videoId']}",
            "thumbnail": i['snippet']['thumbnails']['high']['url']
        } for i in short_vids], # แก้ให้ตรงกับที่ประกาศไว้
        "folders": drive_items
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print("อัปเดตข้อมูลสำเร็จ!")

if __name__ == "__main__":
    main()
