import requests
import json
import gzip
from io import BytesIO

# Güncel gzip sıkıştırmalı kanal listesi kaynağı
DATA_URL = "https://i.mjh.nz/SamsungTVPlus/.channels.json.gz"
PLAYBACK_URL = "https://jmp2.uk/{slug}"
OUTPUT_FILE = "samsung_tv_plus.m3u"

# İndirmek istediğin bölgeler (örnek: 'us', 'gb', 'all')
TARGET_REGIONS = ["all"]

def fetch_and_generate_m3u():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Güncel veri indiriliyor: {DATA_URL}")
    response = requests.get(DATA_URL, headers=headers, timeout=(10, 30))
    response.raise_for_status()

    # Gzip içeriğini açıp JSON olarak okuyoruz
    json_bytes = gzip.GzipFile(fileobj=BytesIO(response.content)).read()
    data = json.loads(json_bytes)

    m3u_lines = ["#EXTM3U\n"]
    channel_count = 0

    regions_data = data.get("regions", {})
    slug_template = data.get("slug", "{id}")

    for region_key, region_val in regions_data.items():
        # Bölge filtresi (TARGET_REGIONS içinde 'all' varsa hepsini alır)
        if "all" not in TARGET_REGIONS and region_key.lower() not in TARGET_REGIONS:
            continue

        channels = region_val.get("channels", {})
        for ch_id, ch in channels.items():
            # Lisans korumalı (DRM) kanalları atla
            if ch.get("license_url"):
                continue

            name = ch.get("name", "Unknown Channel")
            logo = ch.get("logo", "")
            group = ch.get("group", "Samsung TV Plus")
            chno = ch.get("chno", "")

            # Yayın URL'sini oluştur
            slug = slug_template.format(id=ch_id)
            stream_url = PLAYBACK_URL.format(slug=slug)

            tvg_chno = f' tvg-chno="{chno}"' if chno else ""
            
            m3u_lines.append(
                f'#EXTINF:-1 tvg-id="{ch_id}" tvg-logo="{logo}" group-title="{group}"{tvg_chno},{name}\n'
            )
            m3u_lines.append(f"{stream_url}\n\n")
            channel_count += 1

    # Dosyaya kaydet
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print(f"İşlem Tamamlandı! Toplam {channel_count} kanal '{OUTPUT_FILE}' dosyasına yazıldı.")

if __name__ == "__main__":
    fetch_and_generate_m3u()
