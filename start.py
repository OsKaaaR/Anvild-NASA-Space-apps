#!/usr/bin/env python3
"""SkyBlink — Start the web server.
Run: python start.py
Then open: http://localhost:8000
"""
import subprocess
import sys
import os

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root)
    
    print("=" * 60)
    print("  SkyBlink — SPHEREx Sky Explorer")
    print("  NASA Space Apps Cairo 2026")
    print("=" * 60)
    print(f"  Starting server at http://localhost:8000")
    print(f"  Press Ctrl+C to stop")
    print("=" * 60)
    
    import threading
    import webbrowser
    import time
    def _open_browser():
        time.sleep(1.2)
        webbrowser.open("http://localhost:8000")
    threading.Thread(target=_open_browser, daemon=True).start()
    
    cmd = [sys.executable, "-m", "uvicorn", "backend.app:app",
           "--host", "0.0.0.0", "--port", "8000", "--reload",
           "--reload-dir", os.path.join(root, "backend")]
    subprocess.run(cmd, cwd=root)

if __name__ == "__main__":
    main()
