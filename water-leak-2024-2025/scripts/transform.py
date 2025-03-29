import pandas as pd
import re
import argparse
from datetime import datetime
from pathlib import Path

# Set up argument parser
parser = argparse.ArgumentParser(description="Extract humidity data from weather file")
parser.add_argument("--rawdata", help="Input file name in format YYYYMM.txt (absolute or relative path)")
parser.add_argument("--outdir", help="Output directory to save the resulting CSV file")
args = parser.parse_args()

# Resolve paths
rawdata_path = Path(args.rawdata).resolve()
outdir_path = Path(args.outdir).resolve()
outdir_path.mkdir(parents=True, exist_ok=True)  # Create output directory if it doesn't exist

# Extract year and month from filename
YYYYMM = rawdata_path.name.replace('.txt', '')
year = YYYYMM[:4]
month = YYYYMM[4:]

# Read the file
with open(rawdata_path, 'r', encoding='utf-8') as f:
    data = f.read()

# Extract the section for Humidity
humidity_section = re.findall(r"Max\s+Avg\s+Min\n((?:-?\d+\t-?[\d.]+\t-?\d+\n?)+)", data)

if humidity_section:
    lines = humidity_section[2].strip().split("\n")  # The 3rd Max/Avg/Min block is for humidity
    humidity_data = {}

    for i, line in enumerate(lines):
        day = i + 1
        parts = line.strip().split("\t")
        if len(parts) == 3:
            max_h, avg_h, min_h = parts
            humidity_data[i] = {
                'date': f"{year}-{month}-{day:02d}",
                'max': int(max_h),
                'avg': float(avg_h),
                'min': int(min_h)
            }

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(humidity_data, orient='index')
    # print(df)

    # Save to CSV in output directory
    output_filename = outdir_path / f"humidity_{year}_{month}.csv"
    df.to_csv(output_filename, index=None)
    print(f"Saved to {output_filename}")

else:
    print("Humidity section not found in the data.")



# Extract the section for Temperature
temperature_section = re.findall(r"Max\s+Avg\s+Min\n((?:-?\d+\t-?[\d.]+\t-?\d+\n?)+)", data)

if temperature_section:
    lines = temperature_section[0].strip().split("\n")  # The 3rd Max/Avg/Min block is for temperature
    temperature_data = {}

    for i, line in enumerate(lines):
        day = i + 1
        parts = line.strip().split("\t")
        if len(parts) == 3:
            max_h, avg_h, min_h = parts
            temperature_data[i] = {
                'date': f"{year}-{month}-{day:02d}",
                'max': int(max_h),
                'avg': float(avg_h),
                'min': int(min_h)
            }

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(temperature_data, orient='index')
    # print(df)

    # Save to CSV in output directory
    output_filename = outdir_path / f"temperature_{year}_{month}.csv"
    df.to_csv(output_filename, index=None)
    print(f"Saved to {output_filename}")

else:
    print("temperature section not found in the data.")


# Extract the section for Dew Point
dew_point_section = re.findall(r"Max\s+Avg\s+Min\n((?:-?\d+\t-?[\d.]+\t-?\d+\n?)+)", data)

if dew_point_section:
    lines = dew_point_section[1].strip().split("\n")  # The 3rd Max/Avg/Min block is for dew_point
    dew_point_data = {}

    for i, line in enumerate(lines):
        day = i + 1
        parts = line.strip().split("\t")
        if len(parts) == 3:
            max_h, avg_h, min_h = parts
            dew_point_data[i] = {
                'date': f"{year}-{month}-{day:02d}",
                'max': int(max_h),
                'avg': float(avg_h),
                'min': int(min_h)
            }

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(dew_point_data, orient='index')
    # print(df)

    # Save to CSV in output directory
    output_filename = outdir_path / f"dew_point_{year}_{month}.csv"
    df.to_csv(output_filename, index=None)
    print(f"Saved to {output_filename}")

else:
    print("dew_point section not found in the data.")
