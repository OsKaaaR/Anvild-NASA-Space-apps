"""
SkyBlink FastAPI Backend
NASA Space Apps Cairo 2026
"""

import sys
import os
import hashlib
import numpy as np
from typing import Optional, List
from pathlib import Path
from astropy.io import fits
from astropy.wcs import WCS

# Ensure backend dir is on path so pipeline can be imported
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, PROJECT_ROOT)

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# Vercel / serverless: filesystem is read-only except /tmp
_local_cache = os.path.join(PROJECT_ROOT, "cache")
if os.path.isdir(_local_cache):
    CACHE_DIR = _local_cache  # local dev — use existing cache with FITS
else:
    CACHE_DIR = os.path.join("/tmp", "skyblink_cache")

try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except OSError:
    CACHE_DIR = os.path.join("/tmp", "skyblink_cache")
    os.makedirs(CACHE_DIR, exist_ok=True)

try:
    import pipeline
except ImportError:
    try:
        from . import pipeline
    except ImportError:
        try:
            from backend import pipeline
        except ImportError as _pipe_err:
            print(f"[WARNING] pipeline import failed: {_pipe_err}. Using stub fallback.")
            import pipeline_stub as pipeline

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SkyBlink API",
    description="SPHEREx transient detection — NASA Space Apps Cairo 2026",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static frontend
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ---------------------------------------------------------------------------
# In-process cache
# ---------------------------------------------------------------------------

# Key: (ra, dec, fov_arcmin, bandpass)  →  list[dict]  (observations)
_obs_cache: dict = {}
# Key: (uri, cmap) → dict (rendered image payload)
_rendered_cache: dict = {}


def _cache_key(ra: float, dec: float, fov_arcmin: float, bandpass: str) -> tuple:
    return (round(ra, 6), round(dec, 6), round(fov_arcmin, 4), bandpass)


def _get_obs(ra: float, dec: float, fov_arcmin: float, bandpass: str) -> list:
    key = _cache_key(ra, dec, fov_arcmin, bandpass)
    if key not in _obs_cache or not _obs_cache[key]:
        print(f"[cache miss] auto-querying SPHEREx for {key}")
        observations = pipeline.query_spherex(ra, dec, fov_arcmin, bandpass)
        for i, obs in enumerate(observations):
            obs["index"] = i
        _obs_cache[key] = observations
    return _obs_cache[key]


# ---------------------------------------------------------------------------
# Preset targets
# ---------------------------------------------------------------------------

PRESET_TARGETS = [
    {
        "name": "WISE 0855-0714",
        "ra": 133.7854,
        "dec": -7.2444,
        "description": "Track a cold, faint brown dwarf moving across the cosmos",
        "obs_count": 31,
        "category": "Brown Dwarf",
        "scientific_significance": "One of the coldest known sub-stellar objects (~250 K), showing rapid proper motion (~8 arcsec/yr)."
    },
    {
        "name": "Barnard's Star",
        "ra": 269.4521,
        "dec": 4.6933,
        "description": "Investigate one of the fastest-moving stars in the sky",
        "obs_count": 13,
        "category": "High Proper Motion",
        "scientific_significance": "Closest single star to the Sun with an extreme apparent proper motion of 10.3 arcsec/yr."
    },
    {
        "name": "Epsilon Indi B",
        "ra": 330.8407,
        "dec": -56.7867,
        "description": "Explore a cold brown dwarf binary system",
        "obs_count": 18,
        "category": "Binary Sub-stellar",
        "scientific_significance": "Benchmark T1+T6 brown dwarf binary pair orbiting the K-dwarf star Epsilon Indi."
    },
    {
        "name": "RW Aurigae",
        "ra": 83.1421,
        "dec": 30.4015,
        "description": "Investigate a young, highly variable T Tauri star",
        "obs_count": 5,
        "category": "Young Stellar Object",
        "scientific_significance": "Prototypical young pre-main-sequence star undergoing periodic accretion and circumstellar disk occultations."
    },
    {
        "name": "R Draconis",
        "ra": 269.0624,
        "dec": 65.6935,
        "description": "Explore a luminous pulsating giant Mira variable",
        "obs_count": 5,
        "category": "Pulsating Giant",
        "scientific_significance": "Asymptotic giant branch star with large-amplitude infrared pulsations on ~245-day cycles."
    },
    {
        "name": "M101 Pinwheel",
        "ra": 210.8023,
        "dec": 54.3490,
        "description": "Watch a spiral galaxy across multiple SPHEREx epochs",
        "obs_count": 15,
        "category": "Deep Sky Galaxy",
        "scientific_significance": "Face-on grand-design spiral galaxy with resolved star-forming regions and supernova host environments."
    },
]

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health")
def health():
    print("[health] ping")
    return {"status": "ok", "version": "1.0.0", "service": "SkyBlink API"}


@app.get("/api/targets")
def get_targets():
    print("[targets] returning preset targets")
    return PRESET_TARGETS


@app.get("/api/resolve")
def resolve(name: str = Query(..., description="Astronomical object name")):
    print(f"[resolve] name={name!r}")
    try:
        ra, dec = pipeline.resolve_target(name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Name resolution failed: {exc}")
    return {"ra": ra, "dec": dec, "name": name}


@app.get("/api/search")
def search(
    ra: float = Query(...),
    dec: float = Query(...),
    fov_arcmin: float = Query(10.0),
    bandpass: str = Query("SPHEREx-D2"),
):
    print(f"[search] ra={ra} dec={dec} fov={fov_arcmin} bandpass={bandpass}")
    try:
        observations = pipeline.query_spherex(ra, dec, fov_arcmin, bandpass)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"IRSA query failed: {exc}")

    if not observations:
        return {
            "observations": [],
            "count": 0,
            "ra": ra,
            "dec": dec,
            "fov_arcmin": fov_arcmin,
            "epochs": [],
        }

    # Attach index field
    for i, obs in enumerate(observations):
        obs["index"] = i

    # Cache for downstream endpoints
    key = _cache_key(ra, dec, fov_arcmin, bandpass)
    _obs_cache[key] = observations

    # Epoch grouping (returns groups of obs dicts → convert to index lists)
    try:
        epoch_groups = pipeline.group_by_epoch(observations)
        epochs = [[obs["index"] for obs in grp] for grp in epoch_groups]
    except Exception:
        epochs = [list(range(len(observations)))]

    return {
        "observations": observations,
        "count": len(observations),
        "ra": ra,
        "dec": dec,
        "fov_arcmin": fov_arcmin,
        "epochs": epochs,
    }


@app.get("/api/image/{obs_index}")
def get_image(
    obs_index: int,
    ra: float = Query(...),
    dec: float = Query(...),
    fov_arcmin: float = Query(10.0),
    bandpass: str = Query("SPHEREx-D2"),
    cmap: str = Query("inferno"),
    stretch: str = Query("linear"),
    clip_lo: float = Query(2.0),
    clip_hi: float = Query(98.0),
    gamma: float = Query(1.0),
):
    print(f"[image] obs_index={obs_index} ra={ra} dec={dec} cmap={cmap} stretch={stretch} clip={clip_lo}-{clip_hi}%")
    obs_list = _get_obs(ra, dec, fov_arcmin, bandpass)

    if obs_index < 0 or obs_index >= len(obs_list):
        raise HTTPException(
            status_code=422,
            detail=f"obs_index {obs_index} out of range [0, {len(obs_list)-1}]",
        )

    obs = obs_list[obs_index]
    url_hash = hashlib.sha256(obs.get("uri", "").encode()).hexdigest()[:16]

    # Use pre-rendered cache only when defaults are requested
    is_default_enhancement = (
        stretch == "linear" and
        abs(clip_lo - 2.0) < 0.5 and
        abs(clip_hi - 98.0) < 0.5 and
        abs(gamma - 1.0) < 0.05
    )
    render_file = Path(CACHE_DIR) / f"render_{url_hash}_{cmap}.txt"

    if is_default_enhancement and render_file.exists():
        try:
            image_b64 = render_file.read_text(encoding="utf-8")
            return {
                "image_b64": image_b64,
                "obs_date": obs.get("obs_date", ""),
                "mjd": obs.get("mjd", 0.0),
                "uri": obs.get("uri", ""),
                "shape": [98, 98],
                "wcs_center": {"ra": ra, "dec": dec},
            }
        except Exception:
            pass

    # In-memory cache key (includes enhancement params)
    render_key = (obs.get("uri", ""), cmap, stretch, round(clip_lo, 1), round(clip_hi, 1), round(gamma, 2))
    if is_default_enhancement and render_key in _rendered_cache:
        return _rendered_cache[render_key]

    try:
        fits_path = pipeline.download_fits(obs["uri"], CACHE_DIR)
        img = pipeline.load_fits_image(fits_path)
        norm_data = pipeline.normalize_image(
            img["data"],
            stretch=stretch,
            clip_lo=clip_lo,
            clip_hi=clip_hi,
            gamma=gamma,
        )
        image_b64 = pipeline.image_to_png_base64(norm_data, cmap=cmap)
        # Only write pre-rendered cache for default enhancement
        if is_default_enhancement:
            try:
                render_file.write_text(image_b64, encoding="utf-8")
            except Exception:
                pass
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {exc}")

    # WCS center pixel → sky (safely anchored to requested target position)
    try:
        h, w = img["shape"]
        center_sky = img["wcs"].pixel_to_world(w / 2, h / 2)
        sky_ra = float(center_sky.ra.deg)
        sky_dec = float(center_sky.dec.deg)
        # Verify it matches requested field (within 0.5 deg)
        if ((sky_ra - ra)**2 + (sky_dec - dec)**2)**0.5 < 0.5:
            wcs_center = {"ra": sky_ra, "dec": sky_dec}
        else:
            wcs_center = {"ra": ra, "dec": dec}
    except Exception:
        wcs_center = {"ra": ra, "dec": dec}

    payload = {
        "image_b64": image_b64,
        "obs_date": obs.get("obs_date", ""),
        "mjd": obs.get("mjd", 0.0),
        "uri": obs.get("uri", ""),
        "shape": list(img["shape"]),
        "wcs_center": wcs_center,
    }
    _rendered_cache[render_key] = payload
    return payload


@app.get("/api/preload")
def preload_images(
    ra: float = Query(...),
    dec: float = Query(...),
    fov_arcmin: float = Query(10.0),
    bandpass: str = Query("SPHEREx-D2"),
    cmap: str = Query("inferno"),
    stretch: str = Query("linear"),
    clip_lo: float = Query(2.0),
    clip_hi: float = Query(98.0),
    gamma: float = Query(1.0),
    limit: int = Query(25),
):
    """Pre-process frames in batch to enable instant, zero-lag playback."""
    print(f"[preload] ra={ra} dec={dec} limit={limit} stretch={stretch}")
    obs_list = _get_obs(ra, dec, fov_arcmin, bandpass)
    results = {}
    target_count = min(limit, len(obs_list))
    for i in range(target_count):
        try:
            obs = obs_list[i]
            render_key = (obs.get("uri", ""), cmap, stretch, round(clip_lo, 1), round(clip_hi, 1), round(gamma, 2))
            if render_key in _rendered_cache:
                results[i] = _rendered_cache[render_key]
            else:
                fits_path = pipeline.download_fits(obs["uri"], CACHE_DIR)
                img = pipeline.load_fits_image(fits_path)
                norm_data = pipeline.normalize_image(
                    img["data"],
                    stretch=stretch,
                    clip_lo=clip_lo,
                    clip_hi=clip_hi,
                    gamma=gamma,
                )
                image_b64 = pipeline.image_to_png_base64(norm_data, cmap=cmap)
                payload = {
                    "image_b64": image_b64,
                    "obs_date": obs.get("obs_date", ""),
                    "mjd": obs.get("mjd", 0.0),
                    "uri": obs.get("uri", ""),
                    "shape": list(img["shape"]),
                }
                _rendered_cache[render_key] = payload
                results[i] = payload
        except Exception as e:
            print(f"[preload warning] frame {i} failed: {e}")
            continue
    return {"loaded": len(results), "images": results}


@app.get("/api/difference")
def difference(
    ra: float = Query(...),
    dec: float = Query(...),
    fov_arcmin: float = Query(10.0),
    bandpass: str = Query("SPHEREx-D2"),
    ref_index: int = Query(0),
    target_index: int = Query(...),
):
    print(f"[difference] ref={ref_index} target={target_index}")
    obs_list = _get_obs(ra, dec, fov_arcmin, bandpass)
    n = len(obs_list)

    for idx, label in [(ref_index, "ref_index"), (target_index, "target_index")]:
        if idx < 0 or idx >= n:
            raise HTTPException(
                status_code=422,
                detail=f"{label} {idx} out of range [0, {n-1}]",
            )

    if ref_index == target_index:
        raise HTTPException(status_code=422, detail="ref_index and target_index must differ")

    try:
        ref_obs = obs_list[ref_index]
        tgt_obs = obs_list[target_index]

        ref_path = pipeline.download_fits(ref_obs["uri"], CACHE_DIR)
        tgt_path = pipeline.download_fits(tgt_obs["uri"], CACHE_DIR)

        ref_img = pipeline.load_fits_image(ref_path)
        tgt_img = pipeline.load_fits_image(tgt_path)

        # Reproject target onto reference frame
        tgt_reprojected = pipeline.reproject_to_reference(
            tgt_img, ref_img["wcs"], ref_img["shape"]
        )

        diff_result = pipeline.compute_difference(ref_img, tgt_reprojected)
        diff_arr = diff_result["difference"]
        valid_mask = diff_result["valid_mask"]
        stats = diff_result["stats"]

        candidates = pipeline.detect_candidates(diff_arr, valid_mask, ref_img["wcs"])

        norm_diff = pipeline.normalize_image(diff_arr)
        diff_b64 = pipeline.image_to_png_base64(norm_diff, cmap="RdBu_r")

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Difference computation failed: {exc}")

    return {
        "diff_b64": diff_b64,
        "stats": {
            "mean": float(stats["mean"]) if stats["mean"] is not None else None,
            "std": float(stats["std"]) if stats["std"] is not None else None,
            "min": float(stats["min"]) if stats["min"] is not None else None,
            "max": float(stats["max"]) if stats["max"] is not None else None,
        },
        "candidates": candidates,
    }


@app.get("/api/stack")
def stack(
    ra: float = Query(...),
    dec: float = Query(...),
    fov_arcmin: float = Query(10.0),
    bandpass: str = Query("SPHEREx-D2"),
    indices: str = Query(..., description="Comma-separated observation indices"),
):
    print(f"[stack] ra={ra} dec={dec} indices={indices!r}")
    obs_list = _get_obs(ra, dec, fov_arcmin, bandpass)

    try:
        idx_list = [int(x.strip()) for x in indices.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=422, detail="indices must be comma-separated integers")

    if not idx_list:
        raise HTTPException(status_code=422, detail="At least one index required")

    n = len(obs_list)
    for idx in idx_list:
        if idx < 0 or idx >= n:
            raise HTTPException(status_code=422, detail=f"Index {idx} out of range [0, {n-1}]")

    try:
        # Load reference (first) image
        ref_obs = obs_list[idx_list[0]]
        ref_path = pipeline.download_fits(ref_obs["uri"], CACHE_DIR)
        ref_img = pipeline.load_fits_image(ref_path)
        ref_shape = ref_img["shape"]
        ref_wcs = ref_img["wcs"]

        arrays = [ref_img["data"]]

        for idx in idx_list[1:]:
            obs = obs_list[idx]
            fits_path = pipeline.download_fits(obs["uri"], CACHE_DIR)
            img = pipeline.load_fits_image(fits_path)
            reprojected = pipeline.reproject_to_reference(img, ref_wcs, ref_shape)
            arrays.append(reprojected["data"])

        stack_data = np.nanmean(np.stack(arrays, axis=0), axis=0)
        norm_stack = pipeline.normalize_image(stack_data)
        stack_b64 = pipeline.image_to_png_base64(norm_stack, cmap="inferno")

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Stacking failed: {exc}")

    return {"stack_b64": stack_b64, "count": len(idx_list)}


@app.get("/api/pixel-spectrum")
def get_pixel_spectrum(
    ra: float = Query(...),
    dec: float = Query(...),
    fov_arcmin: float = Query(10.0),
    bandpass: str = Query("SPHEREx-D2"),
    obs_index: int = Query(0),
    pixel_x: int = Query(49),
    pixel_y: int = Query(49),
):
    """
    Extract calibrated pixel flux, photometric variance, flags, and local
    Linear Variable Filter (LVF) wavelength for the specified image coordinates.
    """
    obs_list = _get_obs(ra, dec, fov_arcmin, bandpass)
    if not obs_list:
        raise HTTPException(status_code=404, detail="No observations found")

    idx = max(0, min(obs_index, len(obs_list) - 1))
    obs = obs_list[idx]

    try:
        fits_path = pipeline.download_fits(obs["uri"], CACHE_DIR)
        with fits.open(fits_path, memmap=False) as hdul:
            img_data = hdul["IMAGE"].data
            h, w = img_data.shape
            px = max(0, min(pixel_x, w - 1))
            py = max(0, min(pixel_y, h - 1))

            raw_val = img_data[py, px]
            flux = float(raw_val) if np.isfinite(raw_val) else None

            var_val = None
            uncertainty = None
            if "VARIANCE" in hdul:
                v = hdul["VARIANCE"].data[py, px]
                if np.isfinite(v):
                    var_val = float(v)
                    uncertainty = float(np.sqrt(max(0.0, var_val)))

            flag_val = int(hdul["FLAGS"].data[py, px]) if "FLAGS" in hdul else 0
            zodi_val = None
            if "ZODI" in hdul:
                z = hdul["ZODI"].data[py, px]
                if np.isfinite(z):
                    zodi_val = float(z)

            # Linear Variable Filter (LVF) calibrated wavelength (microns)
            # Band 2 spans 1.10 - 1.62 um across focal plane
            wavelength_um = round(1.10 + (1.62 - 1.10) * (1.0 - py / max(1, h - 1)), 4)

            # Extract sky coordinates
            try:
                wcs_obj = WCS(hdul["IMAGE"].header).celestial
                sky = wcs_obj.pixel_to_world(px, py)
                sky_ra = round(float(sky.ra.deg), 6)
                sky_dec = round(float(sky.dec.deg), 6)
            except Exception:
                sky_ra = round(ra, 6)
                sky_dec = round(dec, 6)

        # Multi-epoch photometric history at this exact pixel (up to 15 epochs)
        epoch_series = []
        sample_indices = list(range(min(15, len(obs_list))))
        for s_idx in sample_indices:
            try:
                s_obs = obs_list[s_idx]
                s_path = pipeline.download_fits(s_obs["uri"], CACHE_DIR)
                with fits.open(s_path, memmap=False) as s_hdul:
                    s_val = s_hdul["IMAGE"].data[py, px]
                    epoch_series.append({
                        "obs_index": s_idx,
                        "date": s_obs.get("obs_date", ""),
                        "mjd": s_obs.get("mjd", 0.0),
                        "flux": float(s_val) if np.isfinite(s_val) else None,
                        "valid": bool(np.isfinite(s_val))
                    })
            except Exception:
                continue

        return {
            "pixel_x": px,
            "pixel_y": py,
            "ra": sky_ra,
            "dec": sky_dec,
            "flux": flux,
            "unit": "MJy/sr",
            "uncertainty": uncertainty,
            "flag_value": flag_val,
            "flag_clean": flag_val == 0,
            "zodi_flux": zodi_val,
            "wavelength_um": wavelength_um,
            "bandpass": bandpass,
            "obs_date": obs.get("obs_date", ""),
            "epoch_series": epoch_series,
            "scientific_note": "SPHEREx Level-2 calibrated surface brightness in MJy/sr with Linear Variable Filter (LVF) spatial dispersion."
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Spectrum extraction failed: {exc}")


# ---------------------------------------------------------------------------
# Frontend serving
# ---------------------------------------------------------------------------


@app.get("/Logo.png")
@app.get("/logo.png")
@app.get("/SkyBlink Cosmic Galaxy Logo.png")
@app.get("/SkyBlink%20Cosmic%20Galaxy%20Logo.png")
@app.get("/skyblink_logo.png")
def serve_logo():
    for candidate in [
        os.path.join(FRONTEND_DIR, "SkyBlink Cosmic Galaxy Logo.png"),
        os.path.join(FRONTEND_DIR, "skyblink_logo.png"),
        os.path.join(FRONTEND_DIR, "logo_thumb.png"),
        os.path.join(FRONTEND_DIR, "Logo.png"),
        os.path.join(PROJECT_ROOT, "SkyBlink Cosmic Galaxy Logo.png"),
        os.path.join(PROJECT_ROOT, "Logo.png"),
    ]:
        if os.path.isfile(candidate):
            return FileResponse(candidate, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo not found")


@app.get("/")
@app.get("/app")
def serve_frontend():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        {"message": "SkyBlink API is running. Frontend not yet deployed."},
        status_code=200,
    )


@app.get("/{filename:path}")
def serve_frontend_asset(filename: str):
    target = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(target):
        # Determine media type for common web assets
        media_type = "image/png" if filename.lower().endswith(".png") else None
        return FileResponse(target, media_type=media_type)
    raise HTTPException(status_code=404, detail=f"Asset '{filename}' not found")
