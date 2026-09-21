#!/usr/bin/env python3
"""
Entry-point: install deps if needed, then start the visualizer web server.
Usage:
    python run_visualizer.py          # starts on http://localhost:5000
    python run_visualizer.py --port 8080
"""

import subprocess
import sys
import importlib


def ensure(pkg, pip_name=None):
    try:
        importlib.import_module(pkg)
    except ImportError:
        print(f"Installing {pip_name or pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name or pkg])


if __name__ == "__main__":
    ensure("flask")

    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args()

    import webbrowser, threading, time

    def open_browser():
        time.sleep(1.2)
        webbrowser.open(f"http://{args.host}:{args.port}")

    threading.Thread(target=open_browser, daemon=True).start()

    # Import and run app
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from web.server import app

    print(f"\n🔧 MiniLang Compiler Visualizer")
    print(f"   → http://{args.host}:{args.port}\n")
    app.run(host=args.host, port=args.port, debug=False)
