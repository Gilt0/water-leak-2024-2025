import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import datetime as dt
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess


ANNOTATIONS = [
    ('2024-07-05', 'Visite plombier   - 05/07/2024', 'Colonne humide'),
    ('2024-10-17', 'Visite plombier   - 17/10/2024', 'Colonne humide'),
    ('2025-02-28', 'Départ locataires - 28/02/2025', 'Colonne sèche')
]

PLOT_ORDER = ['humidity', 'temperature', 'dew_point']
COLORS = {
    'humidity': 'blue',
    'temperature': 'red',
    'dew_point': 'purple',
    'condensation': 'green',
    'excess': 'orange'
}
TITLES = {
    'humidity': 'Humidité',
    'temperature': 'Température',
    'dew_point': 'Point de Rosée'
}


def read_variable_series(cleaned_dir, var):
    """
    Read and smooth weekly weather data for a given variable.

    Parameters:
        cleaned_dir (Path): Path to directory with cleaned CSV files.
        var (str): Variable name (humidity, temperature, dew_point).

    Returns:
        tuple: raw df, weekly average df, smoothed LOWESS trend, standard error.
    """
    files = sorted(Path(cleaned_dir).glob(f"{var}_*.csv"))
    dfs = [pd.read_csv(f, parse_dates=['date']).set_index('date') for f in files]
    df = pd.concat(dfs).sort_index()
    weekly = df.resample('W').mean()
    trend = lowess(weekly['avg'], weekly.index.values.astype(float), frac=0.1, return_sorted=False)
    ste = (weekly['avg'] - trend).std()
    return df, weekly, trend, ste


def add_annotations(ax):
    """
    Add vertical lines and annotation labels for key dates.

    Parameters:
        ax (matplotlib.Axes): The plot axis to annotate.
    """
    for date_str, label, wetness in ANNOTATIONS:
        date = pd.to_datetime(date_str)
        ax.axvline(x=date, color='black', linestyle='--', linewidth=2)
        ax.text(date, ax.get_ylim()[0] * 0.35 + ax.get_ylim()[1] * 0.65, label,
                rotation=90, color='black', fontsize=12, fontweight='bold',
                verticalalignment='top', horizontalalignment='right')
        ax.text(date + dt.timedelta(days=10), ax.get_ylim()[0] * 0.45 + ax.get_ylim()[1] * 0.55, wetness,
                rotation=90, color='brown', fontsize=12, fontweight='bold',
                verticalalignment='top', horizontalalignment='right')
        if '17/10/2024' in label:
            ax.text(date + dt.timedelta(days=20), ax.get_ylim()[0] * 0.40 + ax.get_ylim()[1] * 0.60, '(constatée plombier)',
                    rotation=90, color='brown', fontsize=12, fontweight='bold',
                    verticalalignment='top', horizontalalignment='right')


def add_simple_annotations(ax):
    """
    Add vertical lines and dates only.

    Parameters:
        ax (matplotlib.Axes): The plot axis to annotate.
    """
    for date_str, label, wetness in ANNOTATIONS:
        date = pd.to_datetime(date_str)
        ax.axvline(x=date, color='black', linestyle='--', linewidth=2)
        ax.text(date, ax.get_ylim()[0] * 0.25 + ax.get_ylim()[1] * 0.75, label,
                rotation=90, color='black', fontsize=8, fontweight='bold',
                verticalalignment='top', horizontalalignment='right')


def plot_variable(cleaned_dir, var):
    df, weekly, trend, ste = read_variable_series(cleaned_dir, var)

    fig, ax = plt.subplots(figsize=(14, 6))
    # ax.fill_between(df.index, df['min'], df['max'], color='white', alpha=0.3)
    ax.plot(weekly.index, trend, color=COLORS[var], alpha=0.5)
    ax.fill_between(weekly.index, trend - ste, trend + ste, color=COLORS[var], alpha=0.05)

    ax.set_ylabel(f"{TITLES[var]} (°C)" if var != 'humidity' else "Humidité (%)")
    ax.set_xlabel("Date")
    ax.set_title(f"{TITLES[var]} à Paris de Janvier 2024 à fin Mars 2025")

    ax.set_ylim(df['min'].resample('W').mean().min(), df['max'].resample('W').mean().max())

    add_annotations(ax)
    plt.tight_layout()
    plt.savefig(f"data/png/{var}.png")


def plot_condensation_probability(temp_df, dew_df):
    merged = pd.DataFrame(index=temp_df.index)
    merged['delta'] = temp_df['min'] - dew_df['max']

    alpha = 1
    merged['P_condensation'] = 1 / (1 + np.exp(alpha * merged['delta']))

    weekly = merged['P_condensation'].resample('W').mean()
    smoothed = lowess(weekly, weekly.index.values.astype(float), frac=0.1, return_sorted=False)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(weekly.index, smoothed, color=COLORS['condensation'])
    ax.fill_between(weekly.index, smoothed, color=COLORS['condensation'], alpha=0.1)
    ax.set_ylabel("Probabilité de condensation")
    ax.set_xlabel("Date")
    ax.set_ylim(0, 1.05)
    ax.set_title("Probabilité de condensation (logit α=1)à Paris de Janvier 2024 à fin Mars 2025")
    add_annotations(ax)
    plt.tight_layout()
    plt.savefig("data/png/condensation_probability.png")


def plot_excess_dew_vs_tmin(temp_df, dew_df):
    excess = np.maximum(0, dew_df['max'] - temp_df['min'])
    weekly = excess.resample('W').mean()
    smoothed = lowess(weekly, weekly.index.values.astype(float), frac=0.1, return_sorted=False)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(weekly.index, smoothed, color=COLORS['excess'])
    ax.fill_between(weekly.index, smoothed, color=COLORS['excess'], alpha=0.1)
    ax.set_ylabel("Excès de rosée (°C)")
    ax.set_xlabel("Date")
    ax.set_title("Excès de rosée à Paris de Janvier 2024 à fin Mars 2025")
    add_annotations(ax)
    plt.tight_layout()
    plt.savefig("data/png/excess_dew_vs_tmin.png")


def plot_temperature_and_dewpoint(temp_weekly, dew_weekly):
    temp_trend = lowess(temp_weekly['avg'], temp_weekly.index.values.astype(float), frac=0.1, return_sorted=False)
    dew_trend = lowess(dew_weekly['avg'], dew_weekly.index.values.astype(float), frac=0.1, return_sorted=False)
    temp_ste = (temp_weekly['avg'] - temp_trend).std()
    dew_ste = (dew_weekly['avg'] - dew_trend).std()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(temp_weekly.index, temp_trend, label="Température moyenne", color=COLORS['temperature'])
    ax.fill_between(temp_weekly.index, temp_trend - temp_ste, temp_trend + temp_ste, color=COLORS['temperature'], alpha=0.05)

    ax.plot(dew_weekly.index, dew_trend, label="Point de rosée moyen", color=COLORS['dew_point'])
    ax.fill_between(dew_weekly.index, dew_trend - dew_ste, dew_trend + dew_ste, color=COLORS['dew_point'], alpha=0.05)

    ax.set_ylabel("Température (°C)")
    ax.set_xlabel("Date")
    ax.set_title("Température moyenne vs Point de rosée à Paris (Jan 2024 – Mar 2025)")
    ax.legend()
    add_annotations(ax)
    plt.tight_layout()
    plt.savefig("data/png/temperature_vs_dewpoint.png")


def plot_daily_weather(temp_df, dew_df, humidity_df):
    fig, axs = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    axs[2].scatter(temp_df.index, temp_df['avg'], color=COLORS['temperature'], marker='x', alpha=.3)
    axs[2].set_ylabel("Température (°C)")
    # axs[2].set_title("Température quotidienne")

    axs[1].scatter(dew_df.index, dew_df['avg'], color=COLORS['dew_point'], marker='x', alpha=.3)
    axs[1].set_ylabel("Point de rosée (°C)")
    # axs[1].set_title("Point de rosée quotidien")

    axs[0].scatter(humidity_df.index, humidity_df['avg'], color=COLORS['humidity'], marker='x', alpha=.3)
    axs[0].set_ylabel("Humidité (%)")
    axs[0].set_title("Statistiques quotidiennes - moyennes sur la journée")
    axs[2].set_xlabel("Date")

    add_simple_annotations(axs[0])
    add_simple_annotations(axs[1])
    add_simple_annotations(axs[2])

    plt.tight_layout()
    plt.savefig("data/png/daily_weather_combined.png")


def plot_capped_excess_dew_vs_tmin(temp_df, dew_df):
    capped_temp = temp_df['min'].copy()
    capped_temp[capped_temp < 19] = 19
    print(temp_df['min'].values)
    print(capped_temp.values)
    excess = np.maximum(0, dew_df['min'] - capped_temp)
    weekly = excess.resample('W').mean()
    smoothed = lowess(weekly, weekly.index.values.astype(float), frac=0.1, return_sorted=False)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(weekly.index, smoothed, color=COLORS['excess'])
    ax.fill_between(weekly.index, smoothed, color=COLORS['excess'], alpha=0.1)
    ax.set_ylabel("Excès de rosée (°C)")
    ax.set_xlabel("Date")
    ax.set_title("Excès de rosée à Paris de Janvier 2024 à fin Mars 2025")
    add_annotations(ax)
    plt.tight_layout()
    plt.savefig("data/png/excess_dew_vs_tmin_capped.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cleaned-dir", required=True, help="Path to cleaned CSV files")
    args = parser.parse_args()

    cleaned = Path(args.cleaned_dir).resolve()
    temp_df, temp_weekly, *_ = read_variable_series(cleaned, 'temperature')
    dew_df, dew_weekly, *_ = read_variable_series(cleaned, 'dew_point')
    humidity_df, _, _, _ = read_variable_series(cleaned, 'humidity')

    for var in PLOT_ORDER:
        plot_variable(cleaned, var)

    plot_condensation_probability(temp_df, dew_df)
    plot_excess_dew_vs_tmin(temp_df, dew_df)
    plot_temperature_and_dewpoint(temp_weekly, dew_weekly)
    plot_daily_weather(temp_df, dew_df, humidity_df)
    plot_capped_excess_dew_vs_tmin(temp_df, dew_df)