import numpy as np
from pathlib import Path
from obspy import read, Stream
from scipy import signal

def resample_mseed(input_folder, padtype):

    up=5 
    down=1
    input_f = Path(input_folder)
    
    bh_path = input_f / "deglitched_channels" / "BH"
    if bh_path.exists():
        input_folder = bh_path
        output_folder = input_f/"deglitched_channels"/"BH100"
        output_folder.mkdir(exist_ok=True)
    else:
        input_folder = input_f / "3channel" / "BH"
        output_folder = input_f/"3channel"/"BH100"
        output_folder.mkdir(exist_ok=True)
        
    for mseed_path in input_folder.glob("*.mseed"):
        print(f"Processing: {mseed_path.name}")
        st = read(mseed_path)
        new_st = Stream()

        for tr in st:
            data = tr.data
            old_sr = tr.stats.sampling_rate
            duration = tr.stats.endtime - tr.stats.starttime   
        
            resampled = signal.resample_poly(data, up, down, padtype= padtype) #mean also works
        
            new_sr = old_sr * up / down
        
            expected_npts = int(duration * new_sr) + 1
        
            if len(resampled) > expected_npts:
                resampled = resampled[:expected_npts]
                print(f"{tr.id}: trimmed to expected length")
            elif len(resampled) < expected_npts:
                print(f"{tr.id}: shorter than expected, keeping as is")
        
            tr_resampled = tr.copy()
            tr_resampled.data = resampled.astype(np.float32)
            tr_resampled.stats.sampling_rate = new_sr
            tr_resampled.stats.delta = 1.0 / new_sr
            tr_resampled.stats.npts = len(resampled)
            tr_resampled.stats.starttime = tr.stats.starttime  

            new_st.append(tr_resampled)

        output_path = output_folder / f"{mseed_path.stem}_resampled.mseed"
        new_st.write(output_path, format="MSEED")
        print(f"Saved: {output_path}\n")

    return output_folder