import subprocess
from pathlib import Path

RAW_DIR = Path("data/raw")
CLEANED_DIR = Path("data/cleaned")

def batch_process():
    """
    Run transform.py over a batch of monthly raw weather files.
    """
    for year, months in [(2024, range(1, 13)), (2025, range(1, 4))]:
        for month in months:
            month_str = f"{month:02d}"
            input_file = RAW_DIR / f"{year}{month_str}.txt"
            if input_file.exists():
                subprocess.run([
                    "python", "scripts/transform.py",
                    "--rawdata", str(input_file),
                    "--outdir", str(CLEANED_DIR)
                ])
            else:
                print(f"[!] Missing: {input_file}")

if __name__ == "__main__":
    batch_process()