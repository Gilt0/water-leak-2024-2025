import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import datetime as dt
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess

# Argument parser
parser = argparse.ArgumentParser(description="Plot humidity and temperature trends from cleaned CSVs")
parser.add_argument("--cleaned-dir", required=True, help="Path to the folder containing cleaned humidity and temperature CSV files")
args = parser.parse_args()

# Resolve cleaned folder path
cleaned_dir = Path(args.cleaned_dir).resolve()

# Read humidity files
humidity_files = sorted(cleaned_dir.glob("humidity_*.csv"))
if not humidity_files:
    print(f"No humidity CSV files found in {cleaned_dir}")
    exit(1)

humidity_dfs = []
for file in humidity_files:
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df.date)
    df.set_index('Date', inplace=True)
    humidity_dfs.append(df)

humidity_df = pd.concat(humidity_dfs)
humidity_df.sort_index(inplace=True)
humidity_df = humidity_df.drop(columns=['date'])
humidity_weekly = humidity_df.resample('W').mean()

# Read temperature files
temperature_files = sorted(cleaned_dir.glob("temperature_*.csv"))
if not temperature_files:
    print(f"No temperature CSV files found in {cleaned_dir}")
    exit(1)

temperature_dfs = []
for file in temperature_files:
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df.date)
    df.set_index('Date', inplace=True)
    temperature_dfs.append(df)

temperature_df = pd.concat(temperature_dfs)
temperature_df.sort_index(inplace=True)
temperature_df = temperature_df.drop(columns=['date'])
temperature_weekly = temperature_df.resample('W').mean()

# Read temperature files
dew_point_files = sorted(cleaned_dir.glob("dew_point_*.csv"))
if not dew_point_files:
    print(f"No dew point CSV files found in {cleaned_dir}")
    exit(1)


dew_point_dfs = []
for file in dew_point_files:
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df.date)
    df.set_index('Date', inplace=True)
    dew_point_dfs.append(df)

dew_point_df = pd.concat(dew_point_dfs)
dew_point_df.sort_index(inplace=True)
dew_point_df = dew_point_df.drop(columns=['date'])
dew_point_weekly = dew_point_df.resample('W').mean()

# LOWESS smoothing
humidity_trend = lowess(humidity_weekly['avg'], humidity_weekly.index.values.astype(float), frac=0.1, return_sorted=False)
humidity_error = humidity_weekly['avg'] - humidity_trend
humidity_ste = humidity_error.std()

temperature_trend = lowess(temperature_weekly['avg'], temperature_weekly.index.values.astype(float), frac=0.1, return_sorted=False)
temperature_error = temperature_weekly['avg'] - temperature_trend
temperature_ste = temperature_error.std()

dew_point_trend = lowess(dew_point_weekly['avg'], dew_point_weekly.index.values.astype(float), frac=0.1, return_sorted=False)
dew_point_error = dew_point_weekly['avg'] - dew_point_trend
dew_point_ste = dew_point_error.std()

# Plotting
fig, ax1 = plt.subplots(figsize=(14, 6))

# Plot humidity on left axis
ax1.fill_between(humidity_df.index,
                 humidity_df['min'],
                 humidity_df['max'],
                 color='white', alpha=0.3)
ax1.set_ylabel('Humidité (%)')
ax1.plot(humidity_weekly.index, humidity_trend, color='blue', alpha=.5, label='Tendance humidité (LOWESS)')
ax1.fill_between(humidity_weekly.index,
                 humidity_trend - humidity_ste,
                 humidity_trend + humidity_ste,
                 color='blue', alpha=0.05, label='Erreur standard humidité')

# # Plot temperature on right axis
# ax2 = ax1.twinx()
# ax2.set_ylabel('Température (°C)', color='red')
# ax2.plot(temperature_weekly.index, temperature_trend, color='red', alpha=.5, label='Tendance température (LOWESS)')
# ax2.fill_between(temperature_weekly.index,
#                  temperature_trend - temperature_ste,
#                  temperature_trend + temperature_ste,
#                  color='red', alpha=0.05, label='Erreur standard température')

# Add vertical gray dotted lines with text annotations
annotations = [
    ('2024-07-05', 'Visite plombier   - 05/07/2024', 'Colonne humide'),
    ('2024-10-17', 'Visite plombier   - 17/10/2024', 'Colonne humide'),
    ('2025-02-28', 'Départ locataires - 28/02/2025', 'Colonne sèche')
]

for date_str, label, wetness in annotations:
    date = pd.to_datetime(date_str)
    ax1.axvline(x=date, color='black', linestyle='--', linewidth=2)
    ax1.text(date, ax1.get_ylim()[1] * 0.65, label,
             rotation=90, color='black', fontsize=12, fontweight='bold',
             verticalalignment='top', horizontalalignment='right')
    ax1.text(date + dt.timedelta(days=10), ax1.get_ylim()[1] * 0.55, wetness,
             rotation=90, color='brown', fontsize=12, fontweight='bold',
             verticalalignment='top', horizontalalignment='right')
    if label.find('17/10/2024') > -1:
        ax1.text(date + dt.timedelta(days=20), ax1.get_ylim()[1] * 0.60, '(constatée plombier)',
                rotation=90, color='brown', fontsize=12, fontweight='bold',
                verticalalignment='top', horizontalalignment='right')

# Final touches
plt.title('Humidité à Paris de Janvier 2024 à fin mars 2025')
ax1.set_xlabel('Date')
fig.tight_layout()
# plt.show()
plt.savefig('/Users/gil-arnaudcoche/Documents/admin/rue-des-solitaires/water-leak-2024-2025/data/png/humidity.png')

# Plotting
fig, ax1 = plt.subplots(figsize=(14, 6))

# Plot humidity on left axis
ax1.fill_between(temperature_df.index,
                 temperature_df['min'],
                 temperature_df['max'],
                 color='white', alpha=0.3)
ax1.set_ylabel('Temperature (°C)')
ax1.plot(temperature_weekly.index, temperature_trend, color='red', alpha=.5, label='Tendance humidité (LOWESS)')
ax1.fill_between(temperature_weekly.index,
                 temperature_trend - temperature_ste,
                 temperature_trend + temperature_ste,
                 color='red', alpha=0.05, label='Erreur standard humidité')

# # Plot temperature on right axis
# ax2 = ax1.twinx()
# ax2.set_ylabel('Température (°C)', color='red')
# ax2.plot(temperature_weekly.index, temperature_trend, color='red', alpha=.5, label='Tendance température (LOWESS)')
# ax2.fill_between(temperature_weekly.index,
#                  temperature_trend - temperature_ste,
#                  temperature_trend + temperature_ste,
#                  color='red', alpha=0.05, label='Erreur standard température')

# Add vertical gray dotted lines with text annotations
annotations = [
    ('2024-07-05', 'Visite plombier   - 05/07/2024', 'Colonne humide'),
    ('2024-10-17', 'Visite plombier   - 17/10/2024', 'Colonne humide'),
    ('2025-02-28', 'Départ locataires - 28/02/2025', 'Colonne sèche')
]

for date_str, label, wetness in annotations:
    date = pd.to_datetime(date_str)
    ax1.axvline(x=date, color='black', linestyle='--', linewidth=2)
    ax1.text(date, ax1.get_ylim()[1] * 0.65, label,
             rotation=90, color='black', fontsize=12, fontweight='bold',
             verticalalignment='top', horizontalalignment='right')
    ax1.text(date + dt.timedelta(days=10), ax1.get_ylim()[1] * 0.55, wetness,
             rotation=90, color='brown', fontsize=12, fontweight='bold',
             verticalalignment='top', horizontalalignment='right')
    if label.find('17/10/2024') > -1:
        ax1.text(date + dt.timedelta(days=20), ax1.get_ylim()[1] * 0.60, '(constatée plombier)',
                rotation=90, color='brown', fontsize=12, fontweight='bold',
                verticalalignment='top', horizontalalignment='right')

# Final touches
plt.title('Temperature à Paris de Janvier 2024 à fin mars 2025')
ax1.set_xlabel('Date')
fig.tight_layout()
# plt.show()
plt.savefig('/Users/gil-arnaudcoche/Documents/admin/rue-des-solitaires/water-leak-2024-2025/data/png/temperatures.png')


# Plotting
fig, ax1 = plt.subplots(figsize=(14, 6))

# Plot humidity on left axis
ax1.fill_between(dew_point_df.index,
                 dew_point_df['min'],
                 dew_point_df['max'],
                 color='white', alpha=0.3)
ax1.set_ylabel('dew_point (°C)')
ax1.plot(dew_point_weekly.index, dew_point_trend, color='purple', alpha=.5, label='Tendance humidité (LOWESS)')
ax1.fill_between(dew_point_weekly.index,
                 dew_point_trend - dew_point_ste,
                 dew_point_trend + dew_point_ste,
                 color='purple', alpha=0.05, label='Erreur standard humidité')

# # Plot dew_point on right axis
# ax2 = ax1.twinx()
# ax2.set_ylabel('Température (°C)', color='red')
# ax2.plot(dew_point_weekly.index, dew_point_trend, color='red', alpha=.5, label='Tendance température (LOWESS)')
# ax2.fill_between(dew_point_weekly.index,
#                  dew_point_trend - dew_point_ste,
#                  dew_point_trend + dew_point_ste,
#                  color='red', alpha=0.05, label='Erreur standard température')

# Add vertical gray dotted lines with text annotations
annotations = [
    ('2024-07-05', 'Visite plombier   - 05/07/2024', 'Colonne humide'),
    ('2024-10-17', 'Visite plombier   - 17/10/2024', 'Colonne humide'),
    ('2025-02-28', 'Départ locataires - 28/02/2025', 'Colonne sèche')
]

for date_str, label, wetness in annotations:
    date = pd.to_datetime(date_str)
    ax1.axvline(x=date, color='black', linestyle='--', linewidth=2)
    ax1.text(date, ax1.get_ylim()[1] * 0.65, label,
             rotation=90, color='black', fontsize=12, fontweight='bold',
             verticalalignment='top', horizontalalignment='right')
    ax1.text(date + dt.timedelta(days=10), ax1.get_ylim()[1] * 0.55, wetness,
             rotation=90, color='brown', fontsize=12, fontweight='bold',
             verticalalignment='top', horizontalalignment='right')
    if label.find('17/10/2024') > -1:
        ax1.text(date + dt.timedelta(days=20), ax1.get_ylim()[1] * 0.60, '(constatée plombier)',
                rotation=90, color='brown', fontsize=12, fontweight='bold',
                verticalalignment='top', horizontalalignment='right')

# Final touches
plt.title('Point de Rosée à Paris de Janvier 2024 à fin mars 2025')
ax1.set_xlabel('Date')
fig.tight_layout()
# plt.show()
plt.savefig('/Users/gil-arnaudcoche/Documents/admin/rue-des-solitaires/water-leak-2024-2025/data/png/dew_points.png')






# === CALCUL ET PLOT DE LA PROBABILITÉ DE CONDENSATION ===

# On crée une base hebdomadaire commune
merged = pd.DataFrame(index=temperature_weekly.index)
merged['delta'] = temperature_weekly['min'] - dew_point_weekly['max']

# Calcul de la probabilité via fonction logit
alpha = 1
merged['P_condensation'] = 1 / (1 + np.exp(alpha * merged['delta']))

# Lissage LOWESS de la probabilité
smoothed_prob = lowess(merged['P_condensation'], merged.index.values.astype(float), frac=0.1, return_sorted=False)
merged['smoothed'] = smoothed_prob

# Plot
fig, ax1 = plt.subplots(figsize=(14, 6))

ax1.set_ylabel('Probabilité de condensation')
ax1.plot(merged.index, merged['smoothed'], color='green', alpha=.8, label='Probabilité (logit, α=1)')
ax1.fill_between(merged.index, merged['smoothed'], color='green', alpha=0.1)
ax1.set_ylim(0, 1.05)

# Ajout des annotations déjà définies
for date_str, label, wetness in annotations:
    date = pd.to_datetime(date_str)
    ax1.axvline(x=date, color='black', linestyle='--', linewidth=2)
    ax1.text(date, 0.9, label,
             rotation=90, color='black', fontsize=12, fontweight='bold',
             verticalalignment='top', horizontalalignment='right')
    ax1.text(date + dt.timedelta(days=10), 0.75, wetness,
             rotation=90, color='brown', fontsize=12, fontweight='bold',
             verticalalignment='top', horizontalalignment='right')
    if label.find('17/10/2024') > -1:
        ax1.text(date + dt.timedelta(days=20), 0.80, '(constatée plombier)',
                 rotation=90, color='brown', fontsize=12, fontweight='bold',
                 verticalalignment='top', horizontalalignment='right')

plt.title('Probabilité de condensation (logit α=1)\nParis, Janvier 2024 à Mars 2025')
ax1.set_xlabel('Date')
fig.tight_layout()

# Sauvegarde
plt.savefig('/Users/gil-arnaudcoche/Documents/admin/rue-des-solitaires/water-leak-2024-2025/data/png/condensation_probability.png')