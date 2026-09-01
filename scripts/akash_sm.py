import os
import requests

# এখানে আকাশ গো (Akash Go)-এর সঠিক চ্যানেল ID গুলো দিন
CHANNEL_IDS = [
    "1", "2", "3", "4", "5" # আপনার জানা সঠিক ID দিন
]

BASE_URL = "https://kong.akash-go.com/content-detail/pub/api/v6/channels/"
OUTPUT_FILE = "akash_go.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

def generate_playlist():
    playlist_content = "#EXTM3U\n\n"
    has_data = False
    
    for channel_id in CHANNEL_IDS:
        url = f"{BASE_URL}{channel_id}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Fetching ID {channel_id}: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content_data = data.get("data", {})
                
                # API এর কি (key) নাম যাচাই করা
                title = content_data.get("title") or content_data.get("name") or f"Channel {channel_id}"
                logo = content_data.get("poster") or content_data.get("logo") or ""
                group = content_data.get("category") or "General"
                stream_url = content_data.get("streamUrl") or content_data.get("stream_url") or content_data.get("url") or ""
                
                if stream_url:
                    playlist_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{logo}" group-title="{group}",{title}\n'
                    playlist_content += f'{stream_url}\n\n'
                    has_data = True
                else:
                    print(f"No stream URL found for channel {channel_id}. Full response: {content_data}")
        except Exception as e:
            print(f"Error fetching channel {channel_id}: {e}")

    if has_data:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(playlist_content)
        print(f"Playlist successfully saved to {OUTPUT_FILE}")
    else:
        print("No valid channel data was fetched!")

if __name__ == "__main__":
    generate_playlist()
