import os
import requests

# আপনার কাঙ্ক্ষিত চ্যানেল ID গুলো দিন
CHANNEL_IDS = [
    "101", "102", "103"
]

OUTPUT_FILE = "akash_go.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def generate_playlist():
    playlist_content = "#EXTM3U\n\n"
    
    for channel_id in CHANNEL_IDS:
        url = f"https://kong.akash-go.com/content-detail/pub/api/v6/channels/{channel_id}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Checking ID {channel_id} | Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"API Response: {data}")  # লগে দেখার জন্য রেসপন্স প্রিন্ট
                
                content_data = data.get("data", {})
                title = content_data.get("title") or content_data.get("name") or f"Channel {channel_id}"
                logo = content_data.get("poster") or content_data.get("logo") or ""
                group = content_data.get("category") or "General"
                
                # আকাশ গো এপিআই এর সাধারণ ফিল্ড স্ট্রাকচার
                stream_url = (
                    content_data.get("streamUrl") or 
                    content_data.get("stream_url") or 
                    content_data.get("url") or 
                    content_data.get("playUrl") or ""
                )
                
                if stream_url:
                    playlist_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{logo}" group-title="{group}",{title}\n'
                    playlist_content += f'{stream_url}\n\n'
                else:
                    print(f"No valid stream URL key found for channel {channel_id}")
            else:
                print(f"HTTP Error for {channel_id}: {response.status_code}")
        except Exception as e:
            print(f"Error fetching channel {channel_id}: {e}")

    # ফাইলটি অবশ্যই তৈরি হবে যাতে Git commit ফিল্ড না মারে
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(playlist_content)
        
    print(f"File created successfully: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
