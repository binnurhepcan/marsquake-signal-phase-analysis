import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def compare_phase(mseed_path, result_path, phase="P"):
    manual_csv_path = Path(r"\data\events_csv_path")
    manual_picks = pd.read_csv(manual_csv_path)

    picks_path = Path(result_path)
    picks_csv = picks_path/"picks.csv"

    if not picks_csv.exists():
        print(f"No picks file found at {picks_csv}, skipping.")
        return None
    
    phasenet_picks = pd.read_csv(picks_csv)

    mseed_path = Path(mseed_path)
    mseed_csv = mseed_path/"mseed.csv"
    all_events = pd.read_csv(mseed_csv)

    phasenet_picks['file_name'] = phasenet_picks['file_name'].str.replace(r'_.*(?=\.mseed$)', '', regex=True)
    all_events['fname'] = all_events['fname'].str.replace(r'_.*(?=\.mseed$)', '', regex=True)

    df_phase = phasenet_picks[phasenet_picks['phase_type'].str.upper() == phase.upper()].copy()

    df_phase_max = df_phase.loc[df_phase.groupby('file_name')['phase_score'].idxmax()].reset_index(drop=True)

    df_manual_filtered = manual_picks[manual_picks['file_name'].isin(df_phase_max['file_name'])]

    merged = df_phase_max.merge(df_manual_filtered, on="file_name", how="inner")

    phase_cols = [f"{phase.lower()}{i}" for i in range(1, 6)]
    phase_cols.append(f"{phase.lower()}_spectral_start")
    phase_time_col = "phase_time" 

    for col in phase_cols + [phase_time_col]:
        merged[col] = pd.to_datetime(merged[col], errors="coerce").dt.tz_localize(None)

    diffs = merged[phase_cols].subtract(merged[phase_time_col], axis=0).abs()
    diffs = diffs.apply(lambda x: x.dt.total_seconds())

    merged['min_abs_diff'] = diffs.min(axis=1)

    thresholds = [1, 5, 10, 30, 60, 10000]

    merged['diff_class'] = pd.cut(
        merged['min_abs_diff'],
        bins=[0] + thresholds,
        labels=[1,5,10,30,60,">60"],
        include_lowest=True
    )
# ------- TITLE ---------
    channel_map = {
        "BH100": "BH100",
        "BH10":"BH10",
        "BH80":"BH80",
        "BH50":"BH50",
        "BH60":"BH60",
        "BH": "BH",
        "HH": "HH",
        "BL": "BL",
        "HL": "HL"
    }

    channel = next((v for k, v in channel_map.items() if k in str(mseed_path)), "Unknown")
    print("Current channel:", channel)

    
    undetected = all_events.loc[~all_events['fname'].isin(merged['file_name'])]
    print("Total number of events:", len(all_events)) 
    print("Undetected events:", len(undetected))
    print(undetected)
    

    counts = merged['diff_class'].value_counts().sort_index()
    print("Counts per diff_class:")
    print(counts)

    plt.figure(figsize=(8,4))
    counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.xlabel('Min absolute difference class (s)')
    plt.ylabel('Number of events')
    plt.title(f'Event count per diff_class ({phase}-Phase)')
    plt.show()

    plt.figure(figsize=(12,4))
    plt.plot(merged['file_name'], merged['min_abs_diff'], marker='o', linestyle='', alpha=0.7)
    plt.xlabel('Event name')
    plt.ylabel('Min absolute difference (s)')
    plt.title(f'Min absolute difference per event ({phase}-Phase)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    print(merged[['file_name', 'min_abs_diff']])

    return merged