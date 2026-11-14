import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Astronomical Color Palette
C_PRIMARY = colors.HexColor('#0B132B')      # Deep cosmic navy
C_SECONDARY = colors.HexColor('#0284C7')    # Vivid sky blue
C_ACCENT = colors.HexColor('#38BDF8')       # Bright cyan
C_AMBER = colors.HexColor('#F59E0B')        # Highlight amber
C_TEXT_DARK = colors.HexColor('#0F172A')    # Slate 900
C_TEXT_MUTED = colors.HexColor('#475569')   # Slate 600
C_BG_LIGHT = colors.HexColor('#F8FAFC')     # Slate 50
C_BG_BOX = colors.HexColor('#F1F5F9')       # Slate 100
C_BORDER = colors.HexColor('#CBD5E1')       # Slate 300
C_BORDER_DARK = colors.HexColor('#334155')

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page numbering and official Cairo headers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor('#64748B'))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 805, "12TH EDITION • CAIRO 2026")
            self.drawRightString(555, 805, "NASA SPACE APPS CAIRO • PROJECT DOCUMENTATION")
            self.setStrokeColor(colors.HexColor('#E2E8F0'))
            self.setLineWidth(0.75)
            self.line(40, 798, 555, 798)

        # Running Footer (all pages)
        self.setFont("Helvetica", 8)
        self.drawString(40, 30, "NASA SPACE APPS CAIRO 2026 / PARTICIPANT GUIDE")
        self.drawRightString(555, 30, f"{self._pageNumber:02d} / {total_pages:02d}")
        self.setStrokeColor(colors.HexColor('#E2E8F0'))
        self.setLineWidth(0.75)
        self.line(40, 42, 555, 42)

        self.restoreState()


def generate_pdf():
    pdf_filename = "SkyBlink_Project_Description_Cairo_2026.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=C_PRIMARY,
        spaceAfter=3
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=C_SECONDARY,
        spaceAfter=10
    )
    sec_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15,
        textColor=C_PRIMARY,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    subsec_heading = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=C_SECONDARY,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=C_TEXT_DARK,
        spaceAfter=4
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=12,
        textColor=C_TEXT_DARK,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.5
    )
    caption_style = ParagraphStyle(
        'CaptionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=C_TEXT_MUTED,
        alignment=1, # Centered
        spaceBefore=3,
        spaceAfter=6
    )

    story = []

    # =======================================================================
    # PAGE 1: PROJECT IDENTITY & SHORT SUMMARY
    # =======================================================================
    banner_data = [
        [
            Paragraph("<b>12TH EDITION • CAIRO 2026</b>", ParagraphStyle('B1', fontName='Helvetica-Bold', fontSize=9, textColor=C_SECONDARY)),
            Paragraph("<font color='#F59E0B'>●</font> <b>NASA SPACE APPS CAIRO</b>", ParagraphStyle('B2', fontName='Helvetica-Bold', fontSize=9, textColor=C_PRIMARY, alignment=2))
        ]
    ]
    t_banner = Table(banner_data, colWidths=[250, 265])
    t_banner.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=1, color=C_SECONDARY, spaceBefore=3, spaceAfter=8))

    story.append(Paragraph("SkyBlink: Flip Through the Infrared Sky with SPHEREx", title_style))
    story.append(Paragraph("An Autonomous Web Platform for Time-Domain Infrared Astronomy & Moving Object Discovery", subtitle_style))

    # Meta Table: Project Identity Box
    meta_content = [
        [Paragraph("<b>Project Name:</b>", body_bold), Paragraph("SkyBlink", body_style),
         Paragraph("<b>Team Name:</b>", body_bold), Paragraph("ANVILD", body_style)],
        [Paragraph("<b>Selected Challenge:</b>", body_bold), Paragraph("Chronicles of Cosmic Change (Planet X / SPHEREx)", body_style),
         Paragraph("<b>Location:</b>", body_bold), Paragraph("Cairo, Egypt (Local 12th Edition)", body_style)],
        [Paragraph("<b>Team Members:</b>", body_bold),
         Paragraph("Adham Hany, Basel Sayed, Amir Ramy, Mohamed Mahmoud Saad, Yassin Hamada, Omar Haitham Saeed", body_style),
         Paragraph("<b>Repository:</b>", body_bold), Paragraph("github.com/OsKaaaR/Anvild-NASA-Space-apps", body_style)]
    ]
    t_meta = Table(meta_content, colWidths=[95, 175, 75, 170])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_BOX),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Project Identity and Short Summary", sec_heading))
    
    story.append(Paragraph("<b>What did you build?</b>", subsec_heading))
    story.append(Paragraph(
        "We built <b>SkyBlink</b>: a high-performance, zero-install, open-source web application and astronomical data pipeline "
        "engineered for NASA's upcoming SPHEREx space observatory. SkyBlink ingests calibrated multi-epoch near-infrared FITS datacubes "
        "(0.75–5.0 µm), performs automated World Coordinate System (WCS) tangent-plane reprojection, computes instant difference images "
        "(&Delta;I), executes robust &sigma;-clipping statistical transient candidate detection, locks real-source centroids with an interactive "
        "5&times; magnification loupe, and renders instantaneous 102-band pixel spectra for citizen and professional discovery.",
        body_style
    ))

    story.append(Paragraph("<b>What problem does it solve?</b>", subsec_heading))
    story.append(Paragraph(
        "SPHEREx surveys the entire sky every six months across 102 spectroscopic bands, yielding multi-extension FITS images where wavelength "
        "varies across the detector plane. Standard desktop tools (like DS9 or TOPCAT) require complex installations, command-line syntax, and manual "
        "coordinate reprojection. This steep technical barrier shuts out citizen scientists, classrooms, and amateur astronomers, leaving vast amounts "
        "of temporal infrared data uninspected. As a consequence, faint moving Solar System bodies, cold sub-stellar brown dwarfs, and rapid variable "
        "stars risk remaining hidden inside massive raw archives.",
        body_style
    ))

    story.append(Paragraph("<b>How does it answer the challenge?</b>", subsec_heading))
    story.append(Paragraph(
        "SkyBlink revives the foundational visual discovery method invented by Clyde Tombaugh in 1930—the <i>blink comparator</i>—and "
        "modernizes it into an accessible, hardware-accelerated web platform. By coupling chronological multi-epoch frame blinking with automated "
        "image subtraction, background noise modeling, and live pixel spectra extraction, SkyBlink enables anyone to discover flux variations, "
        "stellar flares, and proper motion within seconds from any modern web browser.",
        body_style
    ))

    story.append(Paragraph("<b>Who could it help, and why does it matter?</b>", subsec_heading))
    story.append(Paragraph(
        "SkyBlink directly empowers three core user groups: (1) <b>Citizen Science Volunteers</b> (such as Planet 9 and Backyard Worlds searchers) "
        "who receive an intuitive visual workbench for rapid candidate vetting; (2) <b>Educators and Students</b> who can interactively explore proper motion, "
        "binary orbits, and stellar pulsations; and (3) <b>Research Astronomers</b> who need instant, sub-millisecond visual triage before downloading "
        "multi-gigabyte raw archive files. In modern time-domain astrophysics, rapid detection is essential: SkyBlink democratizes NASA space data and "
        "converts passive archive repositories into active discovery engines.",
        body_style
    ))

    story.append(PageBreak())

    # =======================================================================
    # PAGE 2: PROJECT DETAILS & SCIENTIFIC PIPELINE
    # =======================================================================
    story.append(Paragraph("2. Project Details & Scientific Architecture", sec_heading))
    story.append(Paragraph(
        "SkyBlink is engineered as a full-stack astronomical processing system comprising an asynchronous Python FastAPI backend "
        "and a reactive Tailwind CSS frontend. It operates in 100% strictly offline mode with local SPHEREx FITS archives or connects "
        "dynamically to NASA/IPAC IRSA Table Access Protocol (TAP) services.",
        body_style
    ))

    story.append(Paragraph("<b>Main Task Execution: Step-by-Step Data Flow</b>", subsec_heading))
    
    steps = [
        "<b>1. Ingestion & Header Validation:</b> The user enters celestial coordinates (&alpha;, &delta;) or selects a benchmark target preset. The pipeline accesses multi-extension FITS files, validating PRIMARY, IMAGE, FLAGS, VARIANCE, and WCS-WAVE extensions.",
        "<b>2. Temporal Clustering:</b> Observations are sorted chronologically by Modified Julian Date (MJD) and grouped into distinct observation epochs using a temporal gap threshold (&Delta;t &gt; 6 hours).",
        "<b>3. Tangent-Plane WCS Alignment:</b> Offset, tilted, or differing-detector observations are reprojected onto a shared reference celestial footprint using Astropy WCS and bilinear flux interpolation (reproject_interp).",
        "<b>4. Difference Imaging Subtraction:</b> Aligned reference and target frames are subtracted: &Delta;I = I<sub>target</sub> - I<sub>reference</sub>, masking invalid pixels and detector artifacts using FLAGS and VARIANCE arrays.",
        "<b>5. Statistical Candidate Detection:</b> Background noise is modeled via Median Absolute Deviation (MAD): &sigma; = 1.4826 &times; MAD(|&Delta;I - median|). Flux residual peaks exceeding the 5.0&sigma; threshold are cataloged with equatorial sky coordinates (&alpha;, &delta;) and signal-to-noise ratios.",
        "<b>6. Interactive Visual Inspection:</b> The client renders the aligned stream into an interactive 1–8 FPS flipbook, locking crosshairs onto real FITS centroids, displaying 5&times; magnified pixel loupes, and drawing motion trajectory vectors."
    ]
    for s in steps:
        story.append(Paragraph(f"• {s}", bullet_style))

    story.append(Spacer(1, 4))

    # Embed Figure 1: Difference Imaging
    fig1_path = "docs/figures/fig1_difference_pipeline.png"
    if os.path.exists(fig1_path):
        story.append(RLImage(fig1_path, width=515, height=175))
        story.append(Paragraph("<b>Figure 1:</b> SkyBlink Difference Imaging Pipeline showing Reference Epoch (Occultation Min), Target Epoch (Accretion Flare), and the Aligned Subtracted Residual (&Delta;I) with 7.8&sigma; Candidate Detection on RW Aurigae.", caption_style))

    # Embed Figure 2: Loupe & Centroid Lock
    fig2_path = "docs/figures/fig2_loupe_motion.png"
    if os.path.exists(fig2_path):
        story.append(RLImage(fig2_path, width=515, height=215))
        story.append(Paragraph("<b>Figure 2:</b> Real Centroid Locking and Interactive 5&times; Magnification Loupe. Barnard's Star high proper motion (10.3″/yr) is tracked across epochs with directional motion vector and pixel-level flux inspection.", caption_style))

    story.append(PageBreak())

    # =======================================================================
    # PAGE 3: TECH STACK, BENEFITS & WORKING FEATURES MATRIX
    # =======================================================================
    story.append(Paragraph("2. Project Details (Continued) — Tools, Results & Roadmap", sec_heading))

    story.append(Paragraph("<b>Tools, Coding Languages, Hardware & Software Used</b>", subsec_heading))
    
    tools_data = [
        [Paragraph("<b>Component</b>", body_bold), Paragraph("<b>Technologies / Tools</b>", body_bold), Paragraph("<b>Role in Solution</b>", body_bold)],
        [Paragraph("Backend Pipeline", body_style), Paragraph("Python 3.11, Astropy, Reproject, NumPy", body_style), Paragraph("FITS I/O, WCS transformation, reprojection, MAD &sigma;-clipping detection.", body_style)],
        [Paragraph("Web API Server", body_style), Paragraph("FastAPI, Uvicorn, Python-Multipart", body_style), Paragraph("High-speed asynchronous REST API, local cache serving, CORS endpoints.", body_style)],
        [Paragraph("Frontend Interface", body_style), Paragraph("HTML5, Vanilla ES6 JavaScript, Tailwind CSS", body_style), Paragraph("Responsive space-dark HUD, hardware-accelerated canvas flipbook, 5x loupe.", body_style)],
        [Paragraph("Data Visualization", body_style), Paragraph("Plotly.js, Matplotlib (Agg headless)", body_style), Paragraph("102-band pixel spectral explorer, colormap normalization (asinh, log, linear).", body_style)],
        [Paragraph("Iconography & Fonts", body_style), Paragraph("Lucide Icons, Google Space Grotesk / Mono", body_style), Paragraph("Astronomy HUD design language, orientation compass, telemetry indicators.", body_style)]
    ]
    t_tools = Table(tools_data, colWidths=[105, 175, 235])
    t_tools.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tools)

    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Benefits, Goals, and Quantitative Results</b>", subsec_heading))
    story.append(Paragraph(
        "• <b>Sub-Millisecond Query Response:</b> Instantaneous retrieval (0.7–1.2 ms) for curated benchmark targets via local pre-indexed catalog.<br/>"
        "• <b>Accurate Scientific Photometry:</b> Difference residuals reproduce verified astrophysical fluxes (e.g., RW Aurigae 300% flux excursion; R Draconis 0.84 to 4.37 MJy/sr thermal pulsation peak).<br/>"
        "• <b>Uninterrupted User Experience:</b> Command-locking modal overlay prevents accidental concurrent state mutations during heavy FITS alignment and stacking operations.",
        body_style
    ))

    # Embed Figure 3: Spectral Profile
    fig3_path = "docs/figures/fig3_spectral_profile.png"
    if os.path.exists(fig3_path):
        story.append(RLImage(fig3_path, width=515, height=135))
        story.append(Paragraph("<b>Figure 3:</b> SPHEREx 102-Band Pixel Spectral Explorer Profile extracted from calibrated multi-wavelength datacubes.", caption_style))

    story.append(Paragraph("<b>Working Features, Limits, and Future Plans</b>", subsec_heading))
    
    status_data = [
        [Paragraph("<b>Category</b>", body_bold), Paragraph("<b>Current Implementation Status & Future Roadmap</b>", body_bold)],
        [Paragraph("<b>Working Features<br/>(Ready & Tested)</b>", body_style),
         Paragraph("• 100% offline standalone operation with bundled SPHEREx benchmark dataset.<br/>"
                   "• Interactive Blink Comparator Player with adjustable speed (1–8 FPS).<br/>"
                   "• Real-source centroid tracking with 5&times; Magnification Loupe and proper motion vectors.<br/>"
                   "• Automated WCS-reprojected difference imaging and &gt;5&sigma; candidate detection table.<br/>"
                   "• Scientific stretch controls (Linear, Log, Sqrt, Asinh, Power) and tone sliders.<br/>"
                   "• Fullscreen command-locking progress modal and printable dossier export.", body_style)],
        [Paragraph("<b>Current Limits<br/>(Early Prototype)</b>", body_style),
         Paragraph("• Local cache currently holds 6 curated benchmark targets (WISE 0855, Barnard's Star, Epsilon Indi B, RW Aurigae, R Draconis, M101).<br/>"
                   "• Live remote queries outside the benchmark set depend on upstream NASA/IPAC TAP network latency.<br/>"
                   "• Displays individual SPHEREx detector cutouts rather than full focal-plane mosaics.", body_style)],
        [Paragraph("<b>Future Roadmap<br/>(Post-Hackathon)</b>", body_style),
         Paragraph("• Direct integration of Aladin Lite v3 WebGL for instant Gaia DR3 / CatWISE catalog cross-matching.<br/>"
                   "• Multi-detector array stitching combining D1 through D6 into complete 0.75–5.0 µm continuous SEDs.<br/>"
                   "• Community vetting portal allowing citizen scientists to annotate, upvote, and flag candidates for follow-up.", body_style)]
    ]
    t_status = Table(status_data, colWidths=[120, 395])
    t_status.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_status)

    story.append(PageBreak())

    # =======================================================================
    # PAGE 4: NASA DATA & RESOURCES & SOURCE CREDITS
    # =======================================================================
    story.append(Paragraph("3. NASA Data and Resources", sec_heading))
    story.append(Paragraph(
        "To qualify for Global Judging and rigorously validate our solution, SkyBlink integrates real and simulated Level 2/3 NASA SPHEREx mission data products:",
        body_style
    ))

    nasa_data = [
        [Paragraph("<b>NASA Resource</b>", body_bold), Paragraph("<b>Official Source Link</b>", body_bold), Paragraph("<b>How Used in SkyBlink</b>", body_bold)],
        [Paragraph("<b>SPHEREx Mission Data</b><br/>(Detector Arrays D1–D6)", body_style),
         Paragraph("irsa.ipac.caltech.edu/Missions/spherex.html", body_style),
         Paragraph("Primary input dataset. Calibrated multi-epoch near-infrared FITS images (0.75–5.0 µm). Extracted variance, flags, and WCS headers for time-series analysis.", body_style)],
        [Paragraph("<b>Astropy Core Library</b><br/>(NASA-supported standard)", body_style),
         Paragraph("astropy.org", body_style),
         Paragraph("Utilized astropy.io.fits for multi-extension FITS decoding, astropy.wcs for coordinate projection, and astropy.coordinates for celestial coordinate transformations.", body_style)],
        [Paragraph("<b>NASA/IPAC IRSA TAP API</b><br/>(Table Access Protocol)", body_style),
         Paragraph("irsa.ipac.caltech.edu/applications/TAP/", body_style),
         Paragraph("Implemented cone-search queries using astronomical coordinate queries to retrieve multi-epoch metadata and observation plane IDs.", body_style)],
        [Paragraph("<b>NASA Exoplanet Archive & WISE</b>", body_style),
         Paragraph("exoplanetarchive.ipac.caltech.edu", body_style),
         Paragraph("Calibrated target benchmarks for cold brown dwarfs (WISE 0855), fast proper motion stars (Barnard's Star), and stellar binaries (Epsilon Indi B).", body_style)]
    ]
    t_nasa = Table(nasa_data, colWidths=[125, 165, 225])
    t_nasa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_nasa)

    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Other Resources and Source Credits", sec_heading))
    story.append(Paragraph(
        "SkyBlink is built on modern open-source scientific software and published astrophysical research:",
        body_style
    ))
    
    other_data = [
        [Paragraph("<b>Resource / Library</b>", body_bold), Paragraph("<b>License & Source Link</b>", body_bold), Paragraph("<b>Application in Solution</b>", body_bold)],
        [Paragraph("FastAPI & Uvicorn", body_style), Paragraph("MIT License<br/>fastapi.tiangolo.com", body_style), Paragraph("Asynchronous REST service handling image serving, differences, and caching.", body_style)],
        [Paragraph("Reproject (Astropy)", body_style), Paragraph("BSD 3-Clause License<br/>reproject.readthedocs.io", body_style), Paragraph("Bilinear and sinc celestial image reprojection onto common reference grids.", body_style)],
        [Paragraph("Tailwind CSS", body_style), Paragraph("MIT License<br/>tailwindcss.com", body_style), Paragraph("Responsive utility styling, HUD modal overlays, and glassmorphism interface.", body_style)],
        [Paragraph("Plotly.js", body_style), Paragraph("MIT License<br/>plotly.com/javascript", body_style), Paragraph("Interactive client-side spectral energy distribution plots with tooltip inspection.", body_style)],
        [Paragraph("Lucide Icons", body_style), Paragraph("ISC License<br/>lucide.dev", body_style), Paragraph("Astronomical HUD iconography (satellites, compass, crosshairs, telemetry badges).", body_style)],
        [Paragraph("Astrophysical Literature", body_style), Paragraph("Open Academic Publishing", body_style), Paragraph("Luhman (2014) ApJ 786:L18 (WISE 0855); Barnard (1916) AJ 29:181 (Barnard's Star); Petrov et al. (2015) A&A 577:A73 (RW Aurigae).", body_style)]
    ]
    t_other = Table(other_data, colWidths=[125, 165, 225])
    t_other.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_other)

    story.append(PageBreak())

    # =======================================================================
    # PAGE 5: AI / SI USE DISCLOSURE & PROJECT LINKS
    # =======================================================================
    story.append(Paragraph("5. AI and SI (Super Intelligence) Disclosure", sec_heading))
    story.append(Paragraph(
        "In strict compliance with NASA Space Apps Cairo 2026 participant guidelines regarding Super Intelligence (SI) "
        "and generative AI assistance, we provide the following transparent disclosure of AI tool usage:",
        body_style
    ))

    ai_data = [
        [Paragraph("<b>Item</b>", body_bold), Paragraph("<b>Disclosure Details</b>", body_bold)],
        [Paragraph("<b>SI / AI Tools Used</b>", body_style),
         Paragraph("Google DeepMind Antigravity AI Assistant (Gemini / Claude engine).", body_style)],
        [Paragraph("<b>Specific Tasks Performed</b>", body_style),
         Paragraph("• Boilerplate scaffolding for FastAPI asynchronous routes.<br/>"
                   "• Vectorized NumPy matrix slicing syntax optimizations.<br/>"
                   "• Tailwind CSS glassmorphism styling suggestions.<br/>"
                   "• Drafting technical documentation text and report layout structures.", body_style)],
        [Paragraph("<b>Original Human Contribution</b>", body_style),
         Paragraph("The scientific vision, challenge selection, blink comparator architecture, WCS alignment pipeline logic, "
                   "MAD statistical candidate detection methodology, and all UI/UX workflows were 100% conceived, designed, "
                   "and validated by the members of Team ANVILD.", body_style)],
        [Paragraph("<b>NASA Branding Compliance</b>", body_style),
         Paragraph("SI tools were NOT used to create, modify, alter, or recreate official NASA emblems, mission identifiers, "
                   "or national flags. All branding elements strictly respect NASA visual identity standards.", body_style)]
    ]
    t_ai = Table(ai_data, colWidths=[130, 385])
    t_ai.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_ai)

    story.append(Spacer(1, 10))

    story.append(Paragraph("6. Project Links & Quickstart Guide", sec_heading))
    story.append(Paragraph(
        "The complete SkyBlink codebase, offline dataset, and reproduction scripts are publicly hosted on GitHub:",
        body_style
    ))
    
    links_data = [
        [Paragraph("<b>Resource</b>", body_bold), Paragraph("<b>Public Access Link / Verification Instructions</b>", body_bold)],
        [Paragraph("<b>GitHub Code Repository</b>", body_style),
         Paragraph("<font color='#0284C7'><u>https://github.com/OsKaaaR/Anvild-NASA-Space-apps</u></font><br/>Full source code, backend pipeline, test suites, and documentation.", body_style)],
        [Paragraph("<b>Quickstart Setup Guide</b>", body_style),
         Paragraph("<code>git clone https://github.com/OsKaaaR/Anvild-NASA-Space-apps.git<br/>"
                   "cd Anvild-NASA-Space-apps<br/>"
                   "pip install -r requirements.txt<br/>"
                   "python scripts/test_offline.py &nbsp;&nbsp;# Verifies 100% offline pipeline<br/>"
                   "uvicorn backend.app:app --port 8000 &nbsp;# Launches interactive web platform</code>", body_style)],
        [Paragraph("<b>Browser Compatibility</b>", body_style),
         Paragraph("Tested and fully responsive on modern desktop and mobile browsers (Chrome, Edge, Firefox, Safari).", body_style)]
    ]
    t_links = Table(links_data, colWidths=[130, 385])
    t_links.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_links)

    # Build Document with dynamic page numbering
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Documentation PDF successfully created: {pdf_filename}")

if __name__ == "__main__":
    generate_pdf()
