import requests
import json
import os

# Örnek Samsung TV Plus API endpoint'i veya topluluk kaynaklı güncel JSON akış listesi
# NOT: İlgilendiğiniz bölgenin (US, GB vb.) açık API / JSON playlist kaynağını buraya bağlayabilirsiniz.
SAMSUNG_CHANNEL_DATA_URL = "https://raw.githubusercontent.com/matthuisman/ip-tv/main/samsung/us.json" # Örnek kaynak

OUTPUT_FILE = "samsung_tv_plus.m3u"

def fetch_channels():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("Samsung TV Plus kanal verileri çekiliyor...")
    response = requests.get(SAMSUNG_CHANNEL_DATA_URL, headers=headers)
    
    if response.status_code != 200:
        print(f"Hata: Veri çekilemedi (Status Code: {response.status_code})")
        return
    
    channels = response.json()
    
    m3u_content = "#EXTM3U x-tvg-url=\"https://raw.githubusercontent.com/matthuisman/ip-tv/main/samsung/us.xml\"\n\n"
    
    count = 0
    for channel_id, ch in channels.items():
        name = ch.get("name", "Unknown Channel")
        logo = ch.get("logo", "")
        group = ch.get("group", "Samsung TV Plus")
        stream_url = ch.get("url", "")
        
        if not stream_url:
            continue
            
        m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}\n'
        m3u_content += f'{stream_url}\n\n'
        count += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)
        
    print(f"Başarılı! Toplam {count} kanal '{OUTPUT_FILE}' dosyasına yazıldı.")

if __name__ == "__main__":
    fetch_channels()
