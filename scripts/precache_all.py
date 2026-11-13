"""
Pre-download FITS files for SkyBlink key targets to ensure 100% offline, instant playback.
"""
import sys
import os
import concurrent.futures

# Add parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import pipeline

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")

TARGETS = [
    ("WISE 0855-0714", 133.7854, -7.2444, 25), # Primary MVP target
    ("M101", 210.80227, 54.34895, 20),          # Spiral galaxy deep field
    ("Barnard's Star", 269.4521, 4.6933, 10),    # High proper motion
]

def download_one(obs):
    uri = obs["uri"]
    try:
        path = pipeline.download_fits(uri, CACHE_DIR)
        return (uri, True, os.path.basename(path))
    except Exception as e:
        return (uri, False, str(e))

def main():
    print("=" * 60)
    print("SkyBlink Pre-Caching Engine")
    print("=" * 60)

    for name, ra, dec, limit in TARGETS:
        print(f"\n[TARGET] {name} (RA={ra}, Dec={dec}) - Pre-caching up to {limit} frames...")
        try:
            obs_list = pipeline.query_spherex(ra, dec, 10.0, "SPHEREx-D2")
            to_download = obs_list[:limit]
            print(f"  Found {len(obs_list)} observations, downloading first {len(to_download)}...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(download_one, to_download))
                
            success = sum(1 for r in results if r[1])
            print(f"  --> {success}/{len(to_download)} frames ready and cached locally!")
        except Exception as e:
            print(f"  Query error for {name}: {e}")

    print("\nPre-caching complete! All key demonstration frames are in local cache.")

if __name__ == "__main__":
    main()

