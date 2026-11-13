# SkyBlink 🌟

> Explore how the infrared sky changes over time using NASA SPHEREx observations

**NASA Space Apps Cairo 2026** | Challenge: Planet X and SPHEREx

## What is SkyBlink?

SkyBlink is a free, open-source web application that makes NASA's SPHEREx infrared space telescope data accessible to everyone — citizen scientists, students, amateur astronomers, and researchers — without requiring any programming knowledge or manual FITS file processing.

## Features

- 🔭 **Sky Search** — Search by coordinates (RA/Dec) or astronomical object name
- 🎬 **Animated Blink** — Watch the infrared sky change over time as an animated flipbook
- 📊 **Difference Imaging** — Compare epochs to highlight changes
- 🌈 **Stack Mode** — Combine multiple observations for deeper views  
- 🎯 **Candidate Detection** — Automated flagging of potential moving/variable objects
- 🗂️ **Rich Metadata** — Observation dates, detector IDs, wavelength, quality flags
- 📡 **5 Challenge Targets** — Pre-loaded targets from the NASA Space Apps challenge
- 🔗 **Shareable URLs** — Share exact sky views with others
- 📈 **Spectrum Viewer** — SPHEREx spectral information per pixel

## Quick Start

### Prerequisites
- Python 3.10 or later
- Internet connection (for IRSA data access)

### Installation

```bash
# Clone or download the project
cd Skyblink1

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running SkyBlink

```bash
python start.py
```

Then open your browser at: **http://localhost:8000**

Alternatively:
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

## Project Structure

```
Skyblink1/
├── backend/
│   ├── __init__.py
│   ├── app.py          # FastAPI server
│   └── pipeline.py     # SPHEREx data pipeline
├── frontend/
│   └── index.html      # Web interface (single file)
├── cache/              # Downloaded FITS files (auto-created)
├── start.py            # Server launcher
├── requirements.txt
└── README.md
```

## Architecture

### Backend (Python + FastAPI)
The backend handles all SPHEREx data operations:
1. **Name resolution** — Astronomical object name → RA/Dec via Sesame/SIMBAD
2. **IRSA TAP queries** — Query NASA's IRSA database for SPHEREx observations
3. **FITS processing** — Download and process SPHEREx Level-2 FITS files
4. **Image alignment** — Reproject frames onto a common WCS grid
5. **Difference imaging** — Epoch subtraction for change detection
6. **Candidate detection** — Statistical flagging of anomalous pixels

### Frontend (HTML/CSS/JavaScript)
- Single-page application with no build tools required
- Plotly.js for interactive spectrum visualization
- Pure vanilla JavaScript, no framework dependencies

## SPHEREx Data

SkyBlink uses SPHEREx Level-2 (l2b) imaging data accessed via:
- **NASA/IPAC IRSA** at https://irsa.ipac.caltech.edu/
- **TAP service** at https://irsa.ipac.caltech.edu/TAP
- **IBE cutout service** for efficient pixel-level access

### FITS File Structure
Each SPHEREx Level-2 FITS file contains:
- `IMAGE` — Calibrated surface brightness (MJy/sr)
- `FLAGS` — Quality flags (bit-encoded)
- `VARIANCE` — Per-pixel noise estimate
- `ZODI` — Zodiacal light model
- `EPSF` — Point spread function

### Quality Flags
Not all non-zero flag values indicate bad pixels. SkyBlink applies conservative masking of only clearly bad pixels (saturated, cosmic rays) while preserving science-quality marginal pixels.

## Challenge Targets

| Target | RA | Dec | Description |
|--------|-----|-----|-------------|
| WISE 0855-0714 | 133.7854° | -7.2444° | Cold brown dwarf, fastest-moving bright IR source |
| Barnard's Star | 269.4521° | 4.6933° | Closest single star, fastest proper motion |
| Epsilon Indi B | 330.8407° | -56.7867° | Brown dwarf companion |
| RW Aurigae | 83.1421° | 30.4015° | Variable T Tauri star |
| R Draconis | 269.0624° | 65.6935° | Mira variable, infrared bright |

## Scientific Methodology

### Observation Grouping
SPHEREx revisits the same sky region multiple times over its mission. SkyBlink groups observations into "epochs" using a time gap threshold (default: 6 hours). Observations within the same epoch are from the same sky scan.

### Image Alignment
All images are reprojected onto a common tangent-plane WCS grid centered on the target using `astropy.wcs` and the `reproject` library. This ensures that pixel-to-pixel comparisons are geometrically valid.

### Difference Imaging
Difference images are computed by subtracting a reference epoch from subsequent epochs, after alignment. Valid pixels are only those covered in both frames with good quality flags.

### Candidate Detection
Candidates are flagged using a sigma-clipping threshold applied to the difference image. The local noise is estimated using the Median Absolute Deviation (MAD) of the valid difference pixels. Candidates require significance > 5σ by default.

**Important scientific caveat**: Difference image candidates require multi-epoch confirmation and human review before being considered genuine transients or moving objects. Many candidates will be artifacts, noise, or calibration residuals.

## Known Limitations

1. **Data access latency** — Each FITS download from IRSA takes 5-30 seconds depending on network speed. The cache mitigates repeated requests.
2. **Coverage gaps** — Not all sky positions have SPHEREx observations yet. WISE 0855-0714 is the primary validated target.
3. **Spectral WCS** — SPHEREx's 3D spectral data is served as 2D cutouts per band. Full spectrum extraction requires all 102 bands.
4. **Proper motion** — Catalogue overlay proper motion propagation is currently approximated.
5. **Alignment precision** — WCS reprojection accuracy depends on the accuracy of the FITS WCS headers.

## API Reference

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/resolve?name=...` | Resolve object name to coordinates |
| `GET /api/search?ra=...&dec=...&fov_arcmin=...` | Search for observations |
| `GET /api/image/{index}?ra=...&dec=...` | Get processed image |
| `GET /api/difference?ra=...&ref_index=...&target_index=...` | Difference image |
| `GET /api/stack?ra=...&indices=0,1,2` | Stack images |
| `GET /api/targets` | List preset targets |

## Credits

- **Data**: NASA SPHEREx mission, NASA/IPAC IRSA
- **Libraries**: Astropy, Astroquery, Reproject, FastAPI, NumPy, Matplotlib
- **Visualization**: Plotly.js
- **Challenge**: NASA Space Apps Cairo 2026

## License

MIT License — Free to use, modify, and distribute.

