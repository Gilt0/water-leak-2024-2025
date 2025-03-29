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
        ax.text(date, ax.get_ylim()[1] * 0.65, label,
                rotation=90, color='black', fontsize=12, fontweight='bold',
                verticalalignment='top', horizontalalignment='right')
        ax.text(date + dt.timedelta(days=10), ax.get_ylim()[1] * 0.55, wetness,
                rotation=90, color='brown', fontsize=12, fontweight='bold',
                verticalalignment='top', horizontalalignment='right')
        if '17/10/2024' in label:
            ax.text(date + dt.timedelta(days=20), ax.get_ylim()[1] * 0.60, '(constatée plombier)',
                    rotation=90, color='brown', fontsize=12, fontweight='bold',
                    verticalalignment='top', horizontalalignment='right')


def plot_variable(cleaned_dir, var):
    """
    Plot a smoothed trend and variation of a weather variable.

    Parameters:
        cleaned_dir (Path): Path to cleaned CSV directory.
        var (str): Variable name to plot.
    """
    df, weekly, trend, ste = read_variable_series(cleaned_dir, var)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.fill_between(df.index, df['min'], df['max'], color='white', alpha=0.3)
    ax.plot(weekly.index, trend, color=COLORS[var], alpha=0.5)
    ax.fill_between(weekly.index, trend - ste, trend + ste, color=COLORS[var], alpha=0.05)

    ax.set_ylabel(f"{TITLES[var]} (°C)" if var != 'humidity' else "Humidité (%)")
    ax.set_xlabel("Date")
    ax.set_title(f"{TITLES[var]} à Paris de Janvier 2024 à fin mars 2025")

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
    ax.set_title("Probabilité de condensation (logit α=1)à Paris de Janvier 2024 à fin mars 2025")
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
    ax.set_title("Excès de roséeà Paris de Janvier 2024 à fin mars 2025")
    add_annotations(ax)
    plt.tight_layout()
    plt.savefig("data/png/excess_dew_vs_tmin.png")


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
