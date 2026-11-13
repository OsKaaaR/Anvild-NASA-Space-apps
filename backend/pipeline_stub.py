"""
pipeline_stub.py — temporary stub used ONLY for import-time testing.
The real pipeline.py is built by the pipeline worker.
"""

import numpy as np

def resolve_target(name: str):
    return (0.0, 0.0)

def query_spherex(ra, dec, fov_arcmin=10.0, bandpass="SPHEREx-D2"):
    return []

def download_fits(url: str, cache_dir: str):
    return "/tmp/stub.fits"

def load_fits_image(fits_path: str):
    return {"data": np.zeros((10, 10)), "wcs": None, "header": {}, "flags": None, "variance": None, "shape": (10, 10)}

def reproject_to_reference(source, reference_wcs, shape):
    return {"data": np.zeros(shape), "footprint": np.ones(shape), "wcs": reference_wcs}

def compute_difference(img1, img2):
    diff = np.zeros((10, 10))
    return {"difference": diff, "valid_mask": np.ones((10, 10), dtype=bool), "stats": {"mean": 0.0, "std": 1.0, "min": 0.0, "max": 0.0}}

def normalize_image(data, method="percentile"):
    return np.zeros_like(data, dtype=np.float32)

def image_to_png_base64(data, cmap="inferno", vmin=None, vmax=None):
    return "data:image/png;base64,stub"

def group_by_epoch(observations, gap_hours=6.0):
    return [observations]

def detect_candidates(diff_image, valid_mask, wcs, sigma_threshold=5.0):
    return []
