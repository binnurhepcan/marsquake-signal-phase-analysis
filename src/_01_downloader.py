import pandas as pd
from pandas import to_datetime
import numpy as np
import requests
from pathlib import Path
from obspy import read, Stream

def downloader(index_list, p_cut, s_cut, folder_name, csv_file=None):

    if csv_file is None:
        csv_file = r"csv_file_path"

    df = pd.read_csv(csv_file)
    
    for col in [
        "p1","p2","p3","p4","p5","p_spectral_start",
        "s1","s2","s3","s4","s5","s_spectral_start"
    ]:
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    
    df["early_p"] = df[["p1","p2","p3","p4","p5", "p_spectral_start"]].min(axis=1)
    df["latest_s"] = df[["s1","s2","s3","s4","s5", "s_spectral_start"]].max(axis=1)
    
    df["start_download"] = df["early_p"] - pd.Timedelta(seconds=p_cut)
    df["end_download"] = df["latest_s"] + pd.Timedelta(seconds=s_cut)
    
    df.to_csv("to_csv_file_path", index=False)

    selected_events = df.iloc[index_list].copy()

    folder_path = Path(folder_name)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    for _, row in selected_events.iterrows():
        event_name = row["event_id"].split("/")[-1]
        start_str = row["start_download"].strftime("%Y-%m-%dT%H:%M:%S")
        end_str   = row["end_download"].strftime("%Y-%m-%dT%H:%M:%S")
    
        url = f"https://service.iris.edu/fdsnws/dataselect/1/query?net=XB&sta=ELYSE&starttime={start_str}&endtime={end_str}&format=miniseed&nodata=404"
    
        r = requests.get(url)
        if r.status_code == 200:
            with open(f"{folder_path}/{event_name}.mseed", "wb") as f:
                f.write(r.content)
        else:
            print(f"No data for {event_name}")

    output_root = Path(folder_path) / "3channel"
    output_root.mkdir(parents=True, exist_ok=True)
    
    channels = {"HH": 100,"HL": 100,"BH": 20,"BL": 20}
    
    for m_file in folder_path.glob("*.mseed"):
        st = read(m_file)
        original_filename = m_file.name
    
        for prefix, sr in channels.items():
            filtered = Stream(
                tr for tr in st
                if tr.stats.sampling_rate == sr and tr.stats.channel[:2] == prefix
            )
    
            if len(filtered) == 3:
                base_name = original_filename.replace(".mseed", "")
                new_name = f"{base_name}_{prefix}.mseed"

                output_folder = output_root / prefix
                output_folder.mkdir(parents=True, exist_ok=True)
    
                filtered.write(output_folder / new_name, format="MSEED")