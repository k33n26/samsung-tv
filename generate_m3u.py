import requests
import json
import gzip
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

# Tüm kanalları çekeceğimiz güncel veri kaynağı
DATA_URL = "https://i.mjh.nz/SamsungTVPlus/.channels.json.gz"
PLAYBACK_URL = "https://jmp2.uk/{slug}"
OUTPUT_FILE = "samsung_tv_plus.m3u"

# Tüm bölgeleri tarıyoruz
TARGET_REGIONS = ["all"]

# Aynı anda kaç bağlantının test edileceği (Hızlandırmak için paralel istek)
MAX_WORKERS = 15
TIMEOUT_SECONDS = 3

def check_stream(channel_data):
    """
    Kanalın yayın adresine kısa bir HEAD/GET isteği atarak
    Türkiye IP'sinden erişilebilir olup olmadığını (200 OK) test eder.
    """
    ch_id, ch, slug_template = channel_data
    
    # DRM/Lisanslı kanalları direkt atla
    if ch.get("license_url"):
        return None

    slug = slug_template.format(id=ch_id)
    stream_url = PLAYBACK_URL.format(slug=slug)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # Bağlantının canlı ve geo-blocksuz olup olmadığını kontrol et
        res = requests.head(stream_url, headers=headers, timeout=TIMEOUT_SECONDS, allow_redirects=True)
        if res.status_code == 200:
            return (ch_id, ch, stream_url)
        
        # Bazı sunucular HEAD kabul etmezse GET ile kısa bir deneme yap
        res = requests.get(stream_url, headers=headers, timeout=TIMEOUT_SECONDS, stream=True)
        if res.status_code == 200:
            return (ch_id, ch, stream_url)
    except Exception:
        pass

    return None

def fetch_and_generate_m3u():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"Güncel veri indiriliyor: {DATA_URL}")
    response = requests.get(DATA_URL, headers=headers, timeout=(10, 30))
    response.raise_for_status()

    json_bytes = gzip.GzipFile(fileobj=BytesIO(response.content)).read()
    data = json.loads(json_bytes)

    regions_data = data.get("regions", {})
    slug_template = data.get("slug", "{id}")

    candidate_channels = []

    # Bütün bölgelerdeki aday kanalları topla
    for region_key, region_val in regions_data.items():
        channels = region_val.get("channels", {})
        for ch_id, ch in channels.items():
            candidate_channels.append((ch_id, ch, slug_template))

    print(f"Toplam {len(candidate_channels)} kanal bulundu. Bağlantılar test ediliyor...")

    valid_channels = []
    
    # Multithreading kullanarak kanalları hızlıca test et
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(check_stream, item) for item in candidate_channels]
        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_channels.append(result)

    print(f"Test Tamamlandı! {len(valid_channels)} adet çalışan kanal tespit edildi.")

    # M3U İçeriğini Oluştur
    m3u_lines = ["#EXTM3U\n"]
    for ch_id, ch, stream_url in valid_channels:
        name = ch.get("name", "Unknown Channel")
        logo = ch.get("logo", "")
        group = ch.get("group", "Samsung TV Plus")
        chno = ch.get("chno", "")
        tvg_chno = f' tvg-chno="{chno}"' if chno else ""

        m3u_lines.append(
            f'#EXTINF:-1 tvg-id="{ch_id}" tvg-logo="{logo}" group-title="{group}"{tvg_chno},{name}\n'
        )
        m3u_lines.append(f"{stream_url}\n\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print(f"İşlem Tamamlandı! Çalışan kanallar '{OUTPUT_FILE}' dosyasına yazıldı.")

if __name__ == "__main__":
    fetch_and_generate_m3u()
