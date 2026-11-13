# SkyBlink — Competition Pitch & Presentation
## NASA Space Apps Cairo 2026 — Planet X and SPHEREx Challenge

---

### Slide 1: Title & Hook
* **Title**: **SkyBlink: Flip Through the Infrared Sky with SPHEREx**
* **Subtitle**: An Autonomous Web Platform for Time-Domain Infrared Astronomy & Moving Object Discovery
* **Team**: ANVILD (Adham Hany, Basel Sayed, Amir Ramy, Mohamed Mahmoud Saad, Yassin Hamada, Omar Haitham Saeed)
* **Hook**: *"In 1930, Clyde Tombaugh discovered Pluto by clicking back and forth between two photographic glass plates. In 2026, NASA's SPHEREx is mapping billions of objects in 102 infrared bands. But citizen scientists have had no flipbook for this extraordinary telescope — until now."*

---

### Slide 2: The Problem
* **The Opportunity**: SPHEREx maps the entire sky every 6 months in 102 near-infrared bands (0.75–5.0 µm), delivering fresh calibrated images weekly through NASA/IPAC IRSA.
* **The Barrier**: Data is distributed as heavy, multi-extension FITS files where wavelength changes across the detector.
* **The Gap**: Professional archives provide complex search interfaces, but lack interactive temporal flipbooks, image subtraction, or automated change detection on the web. Without an accessible tool, undiscovered brown dwarfs, asteroids, and variable stars stay hidden.

---

### Slide 3: Our Solution — SkyBlink
* A **free, zero-install, open-source web application**:
  * Type an object name or enter RA/Dec.
  * Instant live TAP query to NASA's SPHEREx archive.
  * Animated flipbook player with step, pause, and speed controls.
  * One-click difference imaging with automated transient candidate detection.
  * Interactive on-the-fly pixel spectra using Plotly.js.
  * Shareable, embeddable URLs that encode coordinates, field of view, and display mode.

---

### Slide 4: Scientific Pipeline Architecture
* **Step 1: Ingestion & Verification**: Reads multi-extension FITS (`IMAGE`, `FLAGS`, `VARIANCE`, `ZODI`, `EPSF`, `WCS-WAVE`).
* **Step 2: Epoch Grouping**: Groups observations into distinct visits using temporal clustering ($\Delta t > 6$ hours).
* **Step 3: WCS Alignment**: Reprojects non-overlapping frames onto a shared tangent-plane grid using Astropy WCS and `reproject_interp`.
* **Step 4: Image Subtraction**: Computes $\Delta I = I_{\text{target}} - I_{\text{ref}}$ on valid overlapping footprints.
* **Step 5: Statistical Candidate Detection**: Robust Median Absolute Deviation (MAD) noise modeling flags sources exceeding $5\sigma$ significance with sky coordinates $(\alpha, \delta)$.

---

### Slide 5: Key Features & UX
1. **Interactive Blink Player**: Play, pause, step forward/backward, and adjust frame rate (1 to 8 fps) with hardware-accelerated rendering.
2. **Preset Challenge Targets**: Instant 1-click access to the 5 challenge targets: WISE 0855−0714, Barnard's Star, Epsilon Indi B, RW Aurigae, and R Draconis.
3. **Difference & Stacking Modes**: Instantly toggle between chronological flipbook, epoch subtraction, and signal-to-noise boosting co-addition.
4. **Spectral Inspection**: Click any pixel to plot calibrated infrared flux against wavelength across the SPHEREx bandpass.
5. **Stateful Deep Linking**: Every view, coordinate, and visualization stretch is synchronized in the browser URL for collaboration.

---

### Slide 6: Live Demonstration Walkthrough
1. **Target Selection**: Click the **WISE 0855** preset button ($RA = 133.7854^\circ, Dec = -7.2444^\circ$).
2. **Search**: Click **Search Observations**. SkyBlink queries NASA IRSA live and identifies **48 SPHEREx observations** across **19 distinct epochs**.
3. **Blink Animation**: Press **Space** or the Play button to watch the sky region change over time.
4. **Difference Mode**: Switch to **Difference** mode and select a reference epoch. Observe the aligned subtraction image.
5. **Candidate Discovery**: The Candidates panel immediately lists detected flux anomalies with pixel coordinates, sky coordinates, and statistical significance ($\sigma$).

---

### Slide 7: Scientific Value & Impact
* **Citizen Science**: Empowers the community of Backyard Worlds and Planet 9 volunteers to explore SPHEREx data directly.
* **Education**: Allows students and teachers to demonstrate stellar proper motion, parallax, and infrared variability in real time.
* **Researcher Acceleration**: Provides astronomers with an instant visual quick-look before downloading multi-gigabyte data sets.

---

### Slide 8: Limitations & Future Roadmap
* **Current Limitations**: Live cutout downloads depend on NASA IRSA network response times (mitigated by intelligent local caching).
* **Next Steps**:
  * Direct Aladin Lite v3 WebGL layer embedding for seamless Gaia DR3 and CatWISE catalogue cross-matching.
  * Multi-detector synthesis combining all 6 SPHEREx detector arrays (D1 to D6) into complete 0.75–5.0 µm spectral energy distributions.
  * Citizen science vote and annotation system for candidate vetting.

