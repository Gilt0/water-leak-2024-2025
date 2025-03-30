import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

# --- CONFIGURATION ---
csv_file = "/Users/gil-arnaudcoche/Documents/admin/rue-des-solitaires/water-leak-2024-2025/data/météo-france-historique/H_75_latest-2024-2025.csv"
important_dates = ["2024-07-05", "2024-10-17", "2025-02-28"]
date_format = "%Y%m%d%H"
window_size = 24

# --- LOAD DATA ---
df = pd.read_csv(csv_file, sep=';', dtype=str)
df["T"] = pd.to_numeric(df["T"], errors='coerce')
df["TD"] = pd.to_numeric(df["TD"], errors='coerce')
df["T_C"] = df["T"] # / 10.0
df["TD_C"] = df["TD"] # / 10.0
df["datetime"] = pd.to_datetime(df["AAAAMMJJHH"], format=date_format)
df = df.dropna(subset=["T_C", "TD_C", "datetime"])
df = df.sort_values("datetime")

# --- CENTERED MOVING AVERAGE ---
# df["T_filtered"] = df["T_C"].rolling(window=window_size, center=True).mean()
# df["TD_filtered"] = df["TD_C"].rolling(window=window_size, center=True).mean()
df["T_filtered"] = df["T_C"].rolling(window=window_size).mean()
df["TD_filtered"] = df["TD_C"].rolling(window=window_size).mean()

# --- Clamp filtered temp to min 15°C ---
df["T_filtered_capped10"] = df["T_filtered"].apply(lambda x: max(x, 10) if pd.notnull(x) else np.nan)
df["T_filtered_capped15"] = df["T_filtered"].apply(lambda x: max(x, 15) if pd.notnull(x) else np.nan)

# --- Compute delta: capped filtered temp - dew point ---
df["delta_TD_10"] = df["T_filtered_capped10"] - df["TD_filtered"]
df["delta_TD_15"] = df["T_filtered_capped15"] - df["TD_filtered"]

# --- Plot Style ---
plt.style.use("ggplot")  # similar aesthetics
highlight_color = "red"

def plot_with_highlight(x, y_series, labels, colors, title, ylabel, filename=None):
    plt.figure(figsize=(15, 6))
    
    for y, label, color in zip(y_series, labels, colors):
        plt.plot(x, y, label=label, linewidth=2, color=color)
    
    for date_str in important_dates:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        plt.axvline(x=date_obj, color=highlight_color, linestyle="--", linewidth=1.5)
        plt.text(date_obj, plt.ylim()[1], date_str, color=highlight_color, rotation=90, va='top', fontsize=10)

    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.title(title, fontsize=16, weight="bold")
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300)
        print(f"✅ Saved: {filename}")
    
    # plt.show()


# --- PLOT 1: Outside Temp and Dew Point ---
plot_with_highlight(
    x=df["datetime"],
    y_series=[df["T"], df["TD"]],
    labels=["Outside Temp (°C)", "Dew Point (°C)"],
    colors=["darkorange", "steelblue"],
    title="Outside Temperature and Dew Point",
    ylabel="Temperature (°C)",
    filename="data/png/outside_temp_and_dew_point_15deg_min.png"
)

# --- PLOT 2: Capped Inside Temp and Dew Point ---
plot_with_highlight(
    x=df["datetime"],
    y_series=[df["T_filtered_capped15"], df["TD_filtered"]],
    labels=["Inside Temp at 15°C min (°C)", "Inside Dew Point (°C)"],
    colors=["indianred", "steelblue"],
    title="Inside Temp (°C) and Dew Point",
    ylabel="Temperature (°C)",
    filename="data/png/inside_temp_and_dew_point_15deg_min.png"
)

# --- PLOT 3: Capped Inside Temp and Dew Point ---
plot_with_highlight(
    x=df["datetime"],
    y_series=[df["T_filtered_capped10"], df["TD_filtered"]],
    labels=["Inside Temp at 10°C min (°C)", "Inside Dew Point (°C)"],
    colors=["indianred", "steelblue"],
    title="Inside Temp (°C) and Dew Point",
    ylabel="Temperature (°C)",
    filename="data/png/inside_temp_and_dew_point_10deg_min.png"
)

# --- PLOT 4: Delta Between Temp and Dew Point ---
plot_with_highlight(
    x=df["datetime"],
    y_series=[df["delta_TD_15"]],
    labels=["Temp (≥15°C) - Dew Point"],
    colors=["cadetblue"],
    title="Delta Between Inside Temp and Dew Point",
    ylabel="Inside Temp - Dew Point (°C)",
    filename="data/png/temp_minus_dew_point_delta_15.png"
)

# --- PLOT 5: Delta Between Temp and Dew Point ---
plot_with_highlight(
    x=df["datetime"],
    y_series=[df["delta_TD_10"]],
    labels=["Temp (≥10°C) - Dew Point"],
    colors=["cadetblue"],
    title="Delta Between Inside Temp and Dew Point",
    ylabel="Inside Temp - Dew Point (°C)",
    filename="data/png/temp_minus_dew_point_delta_10.png"
)