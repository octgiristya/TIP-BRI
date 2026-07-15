import urllib.request
import os

ASSETS_DIR = "app/static/vendor"

assets = {
    # Bootstrap
    "bootstrap.min.css": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
    "bootstrap.bundle.min.js": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js",
    # FontAwesome
    "all.min.css": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css",
    # Chart.js
    "chart.umd.js": "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js",
    # ApexCharts
    "apexcharts.min.js": "https://cdn.jsdelivr.net/npm/apexcharts",
    "apexcharts.css": "https://cdn.jsdelivr.net/npm/apexcharts/dist/apexcharts.css",
    # DataTables (Vanilla JS version - simple-datatables)
    "simple-datatables.css": "https://cdn.jsdelivr.net/npm/simple-datatables@9.0.0/dist/style.css",
    "simple-datatables.js": "https://cdn.jsdelivr.net/npm/simple-datatables@9.0.0/dist/umd/simple-datatables.js",
    # Flatpickr
    "flatpickr.min.css": "https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.css",
    "flatpickr.min.js": "https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.js",
    # SweetAlert2
    "sweetalert2.min.css": "https://cdn.jsdelivr.net/npm/sweetalert2@11.10.5/dist/sweetalert2.min.css",
    "sweetalert2.min.js": "https://cdn.jsdelivr.net/npm/sweetalert2@11.10.5/dist/sweetalert2.min.js",
    # Animate.css
    "animate.min.css": "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css",
}

# Webfonts for FontAwesome
fonts_dir = os.path.join(ASSETS_DIR, "webfonts")
os.makedirs(fonts_dir, exist_ok=True)

webfonts = {
    "fa-solid-900.woff2": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/webfonts/fa-solid-900.woff2",
    "fa-regular-400.woff2": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/webfonts/fa-regular-400.woff2",
    "fa-brands-400.woff2": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/webfonts/fa-brands-400.woff2"
}

def download_file(url, dest):
    print(f"Downloading {url} to {dest}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Success: {dest}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    for filename, url in assets.items():
        dest = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(dest):
            download_file(url, dest)
        else:
            print(f"Exists: {dest}")

    for filename, url in webfonts.items():
        dest = os.path.join(fonts_dir, filename)
        if not os.path.exists(dest):
            download_file(url, dest)
        else:
            print(f"Exists: {dest}")
    print("All assets downloaded successfully.")
