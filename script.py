import os, json, requests

YT_KEY = os.getenv("YT_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
DRIVE_FOLDER_ID = "17L88mtW5Nl5Boh9-ETWwVyGHNiUzMnnh" 

def get_yt_data(type_filter, duration_filter):
    all_items = []
    next_page_token = None
    while True:
        url = f"https://www.googleapis.com/youtube/v3/search?key={YT_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=50&type=video&videoDuration={duration_filter}"
        if next_page_token: url += f"&pageToken={next_page_token}"
        res = requests.get(url).json()
        items = res.get('items', [])
        all_items.extend(items)
        next_page_token = res.get('nextPageToken')
        if not next_page_token or len(all_items) >= 200: break
    return all_items

def main():
    # 1. ดึงวิดีโอยาว (Medium/Long)
    long_videos = get_yt_data("video", "medium")
    # 2. ดึง Shorts (Short < 4 นาที ใน API มักรวมอยู่ในกลุ่ม short)
    short_videos = get_yt_data("video", "short")
    # 3. ดึง Drive Folders
    drive_url = f"https://www.googleapis.com/drive/v3/files?q='{DRIVE_FOLDER_ID}'+in+parents+and+mimeType='application/vnd.google-apps.folder'&fields=files(name,webViewLink)&key={YT_KEY}"
    drive_folders = requests.get(drive_url).json().get('files', [])

    # จัดโครงสร้าง JSON ใหม่
    output = {
        "long_videos": [{
            "title": i['snippet']['title'],
            "videoUrl": f"https://www.youtube.com/watch?v={i['id']['videoId']}",
            "thumbnail": i['snippet']['thumbnails']['high']['url']
        } for i in long_videos],
        "shorts": [{
            "title": i['snippet']['title'],
            "videoUrl": f"https://www.youtube.com/watch?v={i['id']['videoId']}",
            "thumbnail": i['snippet']['thumbnails']['high']['url']
        } for i in short_videos],
        "folders": drive_folders
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
