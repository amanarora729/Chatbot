import subprocess
import os
import sys

def main():
    print("Launching Frontend (Streamlit)...")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "streamlit_app/app.py"],
            cwd=root_dir,
            check=True
        )
    except KeyboardInterrupt:
        print("\nFrontend stopped.")

if __name__ == "__main__":
    main()

