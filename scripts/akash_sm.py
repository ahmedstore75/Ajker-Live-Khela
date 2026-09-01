import os
import requests

# চ্যানেলের ID-গুলোর তালিকা
CHANNEL_IDS = [
    "101", "102", "103"  # এখানে আপনার প্রয়োজনীয় আসল চ্যানেল ID গুলো দিয়ে দিন
]

BASE_URL = "https://kong.akash-go.com/content-detail/pub/api/v6/channels/"
OUTPUT_FILE = "akash_go.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json"
}

def generate_playlist():
    playlist_content = "#EXTM3U\n\n"
    
    for channel_id in CHANNEL_IDS:
        url = f"{BASE_URL}{channel_id}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # API এর রেসপন্স স্ট্রাকচার অনুযায়ী ফিল্ডগুলো নেওয়া হচ্ছে
                content_data = data.get("data", {})
                title = content_data.get("title", f"Channel {channel_id}")
                logo = content_data.get("poster", "")
                group = content_data.get("category", "General")
                stream_url = content_data.get("streamUrl", "") # স্ট্রিম লিংকের কি-নেম অনুযায়ী প্রয়োজনমতো পরিবর্তন করতে পারেন
                
                if stream_url:
                    playlist_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{logo}" group-title="{group}",{title}\n'
                    playlist_content += f'{stream_url}\n\n'
                else:
                    print(f"No stream URL found for channel {channel_id}")
            else:
                print(f"Failed to fetch data for ID {channel_id}: Status {response.status_code}")
        except Exception as e:
            print(f"Error fetching channel {channel_id}: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(playlist_content)
        
    print(f"Playlist successfully generated and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
