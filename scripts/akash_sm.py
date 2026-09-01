import os
import random
import json
from datetime import datetime
import requests

BENGALI_KEYWORDS = [
    'somoy', 'jamuna', 'independent', 'dbc', 'ekattor', 'atn', 'channel i', 
    'ntv', 'rtv', 'bangla', 'bd', 'deepto', 'nagorik', 'btv', 'maasranga', 'channel 24'
]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Android 14; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0',
    'okhttp/5.1.0'
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def generate_playlists():
    print("Fetching channels and dynamic cookies...")
    raw_channels = []

    session = requests.Session()

    for channel_id in range(100, 411):
        try:
            api_url = f"https://kong.akash-go.com/content-detail/pub/api/v6/channels/{channel_id}"
            headers = {
                'User-Agent': get_random_user_agent(),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'https://akashgo.com',
                'Referer': 'https://akashgo.com/',
                'x-platform': 'web',
                'x-app-version': '1.0.0',
                'x-device-id': f"web_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))}"
            }

            response = session.get(api_url, headers=headers, timeout=8)
            if response.status_code != 200:
                continue

            res_data = response.json()
            data = res_data.get('data', {})
            
            # ডাটা অবজেক্ট বা চ্যানেল মেটা থেকে ডাটা খোঁজা
            channel_meta = data.get('channelMeta') if isinstance(data, dict) and 'channelMeta' in data else data

            if isinstance(channel_meta, dict):
                channel_name = (channel_meta.get('channelName') or channel_meta.get('name') or channel_meta.get('title') or '').strip()
                logo_url = channel_meta.get('logo') or channel_meta.get('poster') or ""
                
                # একাধিক ফিল্ডের মধ্যে স্ট্রিম ইউআরএল চেক
                stream_url = (
                    channel_meta.get('nonProtectedHlsConsumerUrl') or 
                    channel_meta.get('protectedHlsConsumerUrl') or 
                    channel_meta.get('streamUrl') or 
                    channel_meta.get('url') or 
                    data.get('streamUrl') or ""
                )
                
                category = channel_meta.get('category') or "General"

                # ডায়নামিক কুকি এবং টোকেন এক্সট্র্যাকশন
                dynamic_cookie = ""
                
                # ১. সেসন/রেসপন্স হেডার কুকি চেক
                set_cookie = response.headers.get('set-cookie')
                if set_cookie:
                    dynamic_cookie = set_cookie.split(';')[0]

                # ২. রেসপন্স ডাটা থেকে টোকেন/পলিসি চেক
                if not dynamic_cookie:
                    edge_policy = channel_meta.get('edgePolicy') or data.get('edgePolicy')
                    edge_sig = channel_meta.get('edgeSignature') or data.get('edgeSignature')
                    token = channel_meta.get('token') or data.get('token')
                    
                    if edge_policy and edge_sig:
                        dynamic_cookie = f"Edge-Policy={edge_policy}; Edge-Signature={edge_sig}"
                    elif token:
                        dynamic_cookie = f"Edge-Policy={token}"
                    elif channel_meta.get('cookie'):
                        dynamic_cookie = channel_meta.get('cookie')

                if stream_url and channel_name:
                    raw_channels.append({
                        'name': channel_name,
                        'logo': logo_url,
                        'stream_url': stream_url,
                        'cookie': dynamic_cookie,
                        'category': category
                    })
                    print(f"[✓] Added: {channel_name} | Cookie: {'Yes' if dynamic_cookie else 'No'}")
        except Exception as e:
            pass

    if not raw_channels:
        print("No channels fetched!")
        return

    # ডুপ্লিকেট রিমুভ
    unique_channels = []
    seen_names = set()
    for ch in raw_channels:
        lower_name = ch['name'].lower()
        if lower_name not in seen_names:
            seen_names.add(lower_name)
            unique_channels.append(ch)

    # বাংলা চ্যানেল সর্ট
    def sort_key(ch):
        name_lower = ch['name'].lower()
        cat_lower = ch['category'].lower()
        is_bengali = any(key in name_lower for key in BENGALI_KEYWORDS) or ('bangla' in cat_lower)
        return (0 if is_bengali else 1, ch['name'])

    unique_channels.sort(key=sort_key)

    # ১. M3U তৈরি
    m3u_content = "#EXTM3U\n\n"
    for ch in unique_channels:
        m3u_content += f'#EXTINF:-1 tvg-logo="{ch["logo"]}" group-title="{ch["category"]}",{ch["name"]}\n'
        if ch["cookie"]:
            m3u_content += f'#EXTHTTP:{{"cookie":"{ch["cookie"]}"}}\n'
        m3u_content += f'{ch["stream_url"]}\n\n'

    with open('akash_go.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)

    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)

    # ২. JSON তৈরি
    today = datetime.now().strftime('%Y-%m-%d')
    json_structure = {
        "status": "success",
        "name": "Live Channels",
        "owner": "Ahammad Ali",
        "channels_amount": len(unique_channels),
        "last_update": today,
        "response": [
            {
                "id": idx + 1,
                "name": ch["name"],
                "logo": ch["logo"],
                "stream_url": ch["stream_url"],
                "cookie": ch["cookie"]
            }
            for idx, ch in enumerate(unique_channels)
        ]
    }

    with open('playlist.json', 'w', encoding='utf-8') as f:
        json.dump(json_structure, f, indent=2, ensure_ascii=False)

    print(f"Total {len(unique_channels)} channels saved successfully!")

if __name__ == "__main__":
    generate_playlists()
