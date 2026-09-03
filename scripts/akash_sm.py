import os
import random
import json
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor

BENGALI_KEYWORDS = ['somoy', 'jamuna', 'independent', 'dbc', 'ekattor', 'atn', 'channel i', 'ntv', 'rtv', 'bangla', 'bd', 'deepto', 'nagorik', 'btv', 'maasranga', 'channel 24']
USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36', 'okhttp/5.1.0']

def fetch_single_channel(channel_id):
    try:
        api_url = f"https://kong.akash-go.com/content-detail/pub/api/v6/channels/{channel_id}"
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/json',
            'Origin': 'https://akashgo.com',
            'Referer': 'https://akashgo.com/',
            'x-platform': 'web'
        }

        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None

        res_data = response.json()
        data = res_data.get('data', {})
        channel_meta = data.get('channelMeta') if isinstance(data, dict) and 'channelMeta' in data else data

        if isinstance(channel_meta, dict):
            channel_name = (channel_meta.get('channelName') or channel_meta.get('name') or '').strip()
            logo_url = channel_meta.get('logo') or ""
            stream_url = channel_meta.get('nonProtectedHlsConsumerUrl') or channel_meta.get('protectedHlsConsumerUrl') or channel_meta.get('streamUrl') or ""
            category = channel_meta.get('category') or "General"

            # এপিআই থেকে আসল লাইভ কুকি সংগ্রহ
            real_cookie = ""
            set_cookie = response.headers.get('set-cookie')
            if set_cookie:
                real_cookie = set_cookie.split(';')[0]
            
            if not real_cookie:
                edge_policy = channel_meta.get('edgePolicy') or data.get('edgePolicy')
                edge_sig = channel_meta.get('edgeSignature') or data.get('edgeSignature')
                if edge_policy and edge_sig:
                    real_cookie = f"Edge-Policy={edge_policy}; Edge-Signature={edge_sig}"

            if stream_url and channel_name and real_cookie:
                return {
                    'name': channel_name,
                    'logo': logo_url,
                    'stream_url': stream_url,
                    'cookie': real_cookie,
                    'category': category
                }
    except Exception:
        pass
    return None

def generate_playlists():
    print("Fetching live channels with real API signatures...")
    raw_channels = []

    with ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(fetch_single_channel, range(100, 411))
        for res in results:
            if res:
                raw_channels.append(res)

    if not raw_channels:
        print("Error: No channels with valid live signature were found!")
        return

    m3u_content = "#EXTM3U\n\n"
    for ch in raw_channels:
        m3u_content += f'#EXTINF:-1 tvg-logo="{ch["logo"]}" group-title="{ch["category"]}",{ch["name"]}\n'
        m3u_content += f'#EXTHTTP:{{"cookie":"{ch["cookie"]}"}}\n'
        m3u_content += f'{ch["stream_url"]}\n\n'

    with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)

    print(f"Success! {len(raw_channels)} live channels updated with fresh signatures.")

if __name__ == "__main__":
    generate_playlists()
