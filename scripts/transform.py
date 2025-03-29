import pandas as pd
import re
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

SECTION_INDEX = {
    "temperature": 0,
    "dew_point": 1,
    "humidity": 2
}

def extract_section_data(section_lines, year, month):
    """
    Extracts weather data from a list of tab-separated lines into a DataFrame.

    Parameters:
        section_lines (list): Lines containing tab-separated max, avg, min values.
        year (str): Year of the data.
        month (str): Month of the data.

    Returns:
        pd.DataFrame: DataFrame with date, max, avg, and min columns.
    """
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
    """
    Processes a specific weather variable and saves it as a CSV.

    Parameters:
        data (str): Raw weather text data.
        variable_name (str): Name of the variable (temperature, humidity, etc).
        index (int): Index in the file where the variable appears.
        year (str): Year of the data.
        month (str): Month of the data.
        outdir_path (Path): Path to output directory.
    """
    matches = re.findall(r"Max\s+Avg\s+Min\n((?:-?\d+\t-?[\d.]+\t-?\d+\n?)+)", data)
    if len(matches) > index:
        section = matches[index]
        lines = section.strip().split("\n")
        df = extract_section_data(lines, year, month)
        output_filename = outdir_path / f"{variable_name}_{year}_{month}.csv"
        df.to_csv(output_filename, index=False)
        logging.info(f"{variable_name.capitalize()} saved to {output_filename}")
    else:
        logging.warning(f"{variable_name.capitalize()} section not found.")

def main(rawdata_path: Path, outdir_path: Path):
    """
    Main function to extract all weather variables from a raw data file.

    Parameters:
        rawdata_path (Path): Path to the input .txt file.
        outdir_path (Path): Path to the output directory for CSVs.
    """
    with open(rawdata_path, 'r', encoding='utf-8') as f:
        data = f.read()

    YYYYMM = rawdata_path.stem
    year, month = YYYYMM[:4], YYYYMM[4:]

    for variable, index in SECTION_INDEX.items():
        process_variable(data, variable, index, year, month, outdir_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract weather data to CSV.")
    parser.add_argument("--rawdata", required=True, help="Input .txt file path")
    parser.add_argument("--outdir", required=True, help="Output directory for CSVs")
    args = parser.parse_args()

    rawdata_path = Path(args.rawdata).resolve()
    outdir_path = Path(args.outdir).resolve()
    outdir_path.mkdir(parents=True, exist_ok=True)

    main(rawdata_path, outdir_path)