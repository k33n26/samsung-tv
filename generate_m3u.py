import requests
import os

# Doğrudan çalışan M3U8 kaynağı (Örn: us.m3u8, gb.m3u8 veya tüm kanallar için all.m3u8)
SAMSUNG_M3U_URL = "https://i.mjh.nz/SamsungTVPlus/us.m3u8"
OUTPUT_FILE = "samsung_tv_plus.m3u"

def fetch_m3u():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Samsung TV Plus M3U8 listesi indiriliyor: {SAMSUNG_M3U_URL}")
    response = requests.get(SAMSUNG_M3U_URL, headers=headers)
    
    # HTTP hatası varsa işlemi durdurur
    response.raise_for_status()
    
    # İndirilen M3U içeriğini dosyaya kaydet
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print(f"Başarılı! Liste '{OUTPUT_FILE}' dosyasına yazıldı.")

if __name__ == "__main__":
    fetch_m3u()
