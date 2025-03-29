import pandas as pd
import re
import argparse
from datetime import datetime
from pathlib import Path

# Constants for identifying sections (based on order of appearance in file)
SECTION_INDEX = {
    "temperature": 0,
    "dew_point": 1,
    "humidity": 2
}

def extract_section_data(section_lines, year, month):
    """Extracts structured data from a list of tab-separated lines."""
    data = {}
    for i, line in enumerate(section_lines):
        parts = line.strip().split("\t")
        if len(parts) == 3:
            max_val, avg_val, min_val = parts
            data[i] = {
                'date': f"{year}-{month}-{i+1:02d}",
                'max': int(max_val),
                'avg': float(avg_val),
                'min': int(min_val)
            }
    return pd.DataFrame.from_dict(data, orient='index')


def process_variable(data, variable_name, index, year, month, outdir_path):
    """Processes a specific weather variable and saves to CSV if found."""
    matches = re.findall(r"Max\s+Avg\s+Min\n((?:-?\d+\t-?[\d.]+\t-?\d+\n?)+)", data)
    
    if len(matches) > index:
        section = matches[index]
        lines = section.strip().split("\n")
        df = extract_section_data(lines, year, month)
        output_filename = outdir_path / f"{variable_name}_{year}_{month}.csv"
        df.to_csv(output_filename, index=False)
        print(f"[✓] {variable_name.capitalize()} data saved to {output_filename}")
    else:
        print(f"[!] {variable_name.capitalize()} section not found.")


def main(rawdata_path: Path, outdir_path: Path):
    # Read file content
    with open(rawdata_path, 'r', encoding='utf-8') as f:
        data = f.read()

    # Extract year and month from filename
    YYYYMM = rawdata_path.stem  # removes ".txt"
    year, month = YYYYMM[:4], YYYYMM[4:]

    # Process each variable
    for variable, index in SECTION_INDEX.items():
        process_variable(data, variable, index, year, month, outdir_path)


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Extract weather data (temperature, humidity, dew point) from a raw text file.")
    parser.add_argument("--rawdata", required=True, help="Path to the raw data file (format: YYYYMM.txt)")
    parser.add_argument("--outdir", required=True, help="Directory to save extracted CSV files")
    args = parser.parse_args()

    rawdata_path = Path(args.rawdata).resolve()
    outdir_path = Path(args.outdir).resolve()
    outdir_path.mkdir(parents=True, exist_ok=True)

    main(rawdata_path, outdir_path)