import os
import requests

# ১০০ থেকে ৪১০ পর্যন্ত আইডি জেনারেট করা
CHANNEL_IDS = [str(i) for i in range(100, 411)]

OUTPUT_FILE = "akash_go.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def generate_playlist():
    playlist_content = "#EXTM3U\n\n"
    found_channels = 0
    
    for channel_id in CHANNEL_IDS:
        url = f"https://kong.akash-go.com/content-detail/pub/api/v6/channels/{channel_id}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                content_data = data.get("data", {})
                
                title = content_data.get("title") or content_data.get("name") or f"Channel {channel_id}"
                logo = content_data.get("poster") or content_data.get("logo") or ""
                group = content_data.get("category") or "General"
                
                # সম্ভাব্য স্ট্রিমিং ইউআরএল ফিল্ড চেক
                stream_url = (
                    content_data.get("streamUrl") or 
                    content_data.get("stream_url") or 
                    content_data.get("url") or 
                    content_data.get("playUrl") or ""
                )
                
                if stream_url:
                    playlist_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{logo}" group-title="{group}",{title}\n'
                    playlist_content += f'{stream_url}\n\n'
                    found_channels += 1
                    print(f"Added Channel: {title} (ID: {channel_id})")
        except Exception:
            pass

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(playlist_content)
        
    print(f"Total {found_channels} channels added to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
