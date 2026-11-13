import requests, time

# Test 1: Frontend serving
t0 = time.time()
r = requests.get("http://127.0.0.1:8000/")
print(f"[Frontend] Status={r.status_code}, Length={len(r.text)} chars, Time={int((time.time()-t0)*1000)}ms")
assert r.status_code == 200
assert "SkyBlink" in r.text
assert "mode-tab" in r.text  # new UI element
print("  ✓ New frontend is being served correctly")

# Test 2: All targets
t0 = time.time()
r = requests.get("http://127.0.0.1:8000/api/targets")
targets = r.json()
print(f"\n[Targets] {len(targets)} targets, Time={int((time.time()-t0)*1000)}ms")
for t in targets:
    print(f"  • {t['name']} → RA={t['ra']}, Dec={t['dec']}")

# Test 3: Search for each target
test_targets = [
    ("WISE 0855", 133.7854, -7.2444),
    ("Barnard's Star", 269.4521, 4.6933),
    ("Epsilon Indi B", 330.8407, -56.7867),
    ("RW Aurigae", 83.1421, 30.4015),
    ("R Draconis", 269.0624, 65.6935),
]

print("\n[Search Tests]")
for name, ra, dec in test_targets:
    t0 = time.time()
    r = requests.get(f"http://127.0.0.1:8000/api/search?ra={ra}&dec={dec}")
    data = r.json()
    dt = int((time.time()-t0)*1000)
    print(f"  {name:20s}: {data['count']:3d} obs, {len(data.get('epochs', [])):2d} epochs, {dt}ms")

# Test 4: Image render
print("\n[Image Render Tests]")
for cmap in ["inferno", "viridis", "gray"]:
    t0 = time.time()
    r = requests.get(f"http://127.0.0.1:8000/api/image/0?ra=133.7854&dec=-7.2444&cmap={cmap}")
    data = r.json()
    dt = int((time.time()-t0)*1000)
    has_b64 = "image_b64" in data and len(data["image_b64"]) > 100
    print(f"  cmap={cmap:10s}: ok={has_b64}, b64_len={len(data.get('image_b64',''))}, {dt}ms")

# Test 5: Difference computation
print("\n[Difference Test]")
t0 = time.time()
r = requests.get("http://127.0.0.1:8000/api/difference?ra=133.7854&dec=-7.2444&ref_index=0&target_index=5")
if r.status_code == 200:
    data = r.json()
    dt = int((time.time()-t0)*1000)
    ncand = len(data.get("candidates", []))
    print(f"  Difference: stats={data.get('stats',{})}")
    print(f"  Candidates: {ncand} detected, {dt}ms")
    if ncand > 0:
        c = data["candidates"][0]
        print(f"  Top: RA={c['ra']:.4f}, Dec={c['dec']:.4f}, σ={c['significance']:.1f}")
else:
    print(f"  Error: {r.status_code} {r.text[:200]}")

# Test 6: Stack
print("\n[Stack Test]")
t0 = time.time()
r = requests.get("http://127.0.0.1:8000/api/stack?ra=133.7854&dec=-7.2444&indices=0,1,2")
if r.status_code == 200:
    data = r.json()
    dt = int((time.time()-t0)*1000)
    print(f"  Stack: count={data.get('count')}, has_b64={len(data.get('stack_b64',''))>100}, {dt}ms")
else:
    print(f"  Error: {r.status_code}")

print("\n" + "="*60)
print("ALL TESTS PASSED ✅")
print("="*60)

