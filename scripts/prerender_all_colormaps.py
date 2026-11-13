"""
Pre-renders all observations for all challenge targets across all colormaps.
Saves render_{url_hash}_{cmap}.txt in cache/ so cloud deployments have 100% instant frames
for any colormap and never fall back to incorrect FITS!
"""
import sys, os, hashlib, json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend import pipeline

CACHE_DIR = ROOT_DIR / "cache"
CATALOG_PATH = ROOT_DIR / "data" / "local_catalog.json"

COLORMAPS = ["inferno", "viridis", "magma", "plasma", "gray", "cubehelix", "hot"]

def main():
    print("Loading catalog...")
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    rendered_count = 0
    skipped_count = 0

    for target_key, target_info in catalog.items():
        obs_list = target_info.get("observations", [])
        print(f"\nProcessing target: {target_info.get('name', target_key)} ({len(obs_list)} obs)")
        
        for idx, obs in enumerate(obs_list):
            uri = obs.get("uri", "")
            url_hash = hashlib.sha256(uri.encode()).hexdigest()[:16]
            
            # Check if any FITS file exists for this URI
            try:
                fits_path = pipeline.download_fits(uri, CACHE_DIR)
                img = pipeline.load_fits_image(fits_path)
                norm_data = pipeline.normalize_image(img["data"])
            except Exception as e:
                print(f"  Warning: could not load FITS for obs {idx} ({uri}): {e}")
                continue

            for cmap in COLORMAPS:
                render_file = CACHE_DIR / f"render_{url_hash}_{cmap}.txt"
                if render_file.exists() and render_file.stat().st_size > 100:
                    skipped_count += 1
                    continue

                try:
                    b64 = pipeline.image_to_png_base64(norm_data, cmap=cmap)
                    render_file.write_text(b64, encoding="utf-8")
                    rendered_count += 1
                except Exception as e:
                    print(f"  Error rendering {cmap} for {url_hash}: {e}")

    print(f"\nDone! Rendered: {rendered_count}, Already Cached: {skipped_count}")

if __name__ == "__main__":
    main()
