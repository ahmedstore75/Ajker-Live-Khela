import os
import random
import json
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor

BENGALI_KEYWORDS = [
    'somoy', 'jamuna', 'independent', 'dbc', 'ekattor', 'atn', 'channel i', 
    'ntv', 'rtv', 'bangla', 'bd', 'deepto', 'nagorik', 'btv', 'maasranga', 'channel 24'
]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Android 14; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0',
    'okhttp/5.1.0'
]

DEFAULT_COOKIE = "Edge-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9vd3Jjb3ZjcnB5LmdwY2RuLm5ldC9icGstdHYvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiRWRnZVRpbWUiOjE3ODgyNTMyMzd9fX1dfQ;Edge-Signature=V3G6GBiA2N6wlM8aLqfdsv1kOW8Z1pxEZgL9GwEuiIs"

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def fetch_single_channel(channel_id):
    try:
        api_url = f"https://kong.akash-go.com/content-detail/pub/api/v6/channels/{channel_id}"
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://akashgo.com',
            'Referer': 'https://akashgo.com/',
            'x-platform': 'web',
            'x-app-version': '1.0.0',
            'x-device-id': f"web_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))}"
        }

        response = requests.get(api_url, headers=headers, timeout=3)
        if response.status_code != 200:
            return None

        res_data = response.json()
        data = res_data.get('data', {})
        channel_meta = data.get('channelMeta') if isinstance(data, dict) and 'channelMeta' in data else data

        if isinstance(channel_meta, dict):
            channel_name = (channel_meta.get('channelName') or channel_meta.get('name') or channel_meta.get('title') or '').strip()
            logo_url = channel_meta.get('logo') or channel_meta.get('poster') or ""
            stream_url = (
                channel_meta.get('nonProtectedHlsConsumerUrl') or 
                channel_meta.get('protectedHlsConsumerUrl') or 
                channel_meta.get('streamUrl') or 
                channel_meta.get('url') or 
                data.get('streamUrl') or ""
            )
            category = channel_meta.get('category') or "General"

            dynamic_cookie = ""
            set_cookie = response.headers.get('set-cookie')
            if set_cookie:
                dynamic_cookie = set_cookie.split(';')[0]

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

            final_cookie = dynamic_cookie if dynamic_cookie else DEFAULT_COOKIE

            if stream_url and channel_name:
                print(f"[+] Found Channel: {channel_name}")
                return {
                    'name': channel_name,
                    'logo': logo_url,
                    'stream_url': stream_url,
                    'cookie': final_cookie,
                    'category': category
                }
    except Exception:
        pass
    return None

def generate_playlists():
    print("Fetching channels rapidly using Multithreading...")
    raw_channels = []

    # ৫০টি থ্রেড একসাথে কাজ করবে, ফলে ১০০-৪১০ চ্যানেল ১০-১৫ সেকেন্ডে কমপ্লিট হবে
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(fetch_single_channel, range(100, 411))
        for res in results:
            if res:
                raw_channels.append(res)

    if not raw_channels:
        print("No channels fetched! Network problem or Akash Go API down.")
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
        m3u_content += f'#EXTHTTP:{{"cookie":"{ch["cookie"]}"}}\n'
        m3u_content += f'{ch["stream_url"]}\n\n'

    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)

    # ২. JSON তৈরি
    today = datetime.now().strftime('%Y-%m-%d')
    json_structure = {
        "status": "success",
        "name": "Live Channels",
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

    print(f"\nSUCCESS! Total {len(unique_channels)} channels saved in 'playlist.m3u' and 'playlist.json'.")

if __name__ == "__main__":
    generate_playlists()
