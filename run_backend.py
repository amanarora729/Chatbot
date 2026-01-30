import subprocess
import os
import sys

def main():
    print("Launching Backend (FastAPI)...")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=root_dir,
            check=True
        )
    except KeyboardInterrupt:
        print("\nBackend stopped.")

if __name__ == "__main__":
    main()

