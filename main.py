"""
SENTINEL-RISK | Main Application Entry Point.
S&P Global & CRISIL Campus Hackathon

Usage:
  python main.py               # Launches the Streamlit Executive Dashboard (Default)
  python main.py --mode api    # Launches the FastAPI REST Backend
  python main.py --mode test   # Runs the 14/14 automated verification test suite
"""

import sys
import subprocess
import argparse


def launch_dashboard():
    """Launches the Streamlit executive risk terminal."""
    print("=" * 65)
    print("🚀 Launching Sentinel-Risk Streamlit Executive Dashboard...")
    print("   URL: http://localhost:8501")
    print("=" * 65)
    cmd = [sys.executable, "-m", "streamlit", "run", "src/dashboard/app.py"]
    subprocess.run(cmd)


def launch_api():
    """Launches the FastAPI backend server with Swagger docs."""
    print("=" * 65)
    print("🚀 Launching Sentinel-Risk FastAPI REST Services...")
    print("   Swagger Docs: http://127.0.0.1:8000/docs")
    print("   Health Check: http://127.0.0.1:8000/health")
    print("=" * 65)
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=False)


def run_tests():
    """Runs the system verification suite."""
    from tests.run_tests import run_all_tests
    run_all_tests()


def main():
    parser = argparse.ArgumentParser(
        description="Sentinel-Risk Platform Launcher | S&P Global & CRISIL Campus Hackathon"
    )
    parser.add_argument(
        "--mode",
        choices=["dashboard", "api", "test"],
        default="dashboard",
        help="Execution mode: 'dashboard' (Streamlit UI, default), 'api' (FastAPI server), 'test' (Test suite)"
    )
    args = parser.parse_args()

    if args.mode == "dashboard":
        launch_dashboard()
    elif args.mode == "api":
        launch_api()
    elif args.mode == "test":
        run_tests()


if __name__ == "__main__":
    main()
