from obspy import read, Stream
from scipy.signal import butter, filtfilt
from pathlib import Path
import numpy as np

def filtering(input_folder, trim, filter_type=None, cutoff=None, order=4, normalize=True):
 
    input_folder = Path(input_folder)
    output_folder = input_folder/"filtered"
    output_folder.mkdir(parents=True, exist_ok=True)
    
    for mseed_file in input_folder.glob("*.mseed"):
        print(f"Processing {mseed_file.name}")
        st = read(mseed_file)
        new_st = Stream()
        
        for tr in st:
            fs = tr.stats.sampling_rate
            data = tr.data.astype(float) #to avoid rounding etc.
            if trim > 0:
                trimming = int(trim * fs)
                data = data[trimming: -trimming]
                tr.stats.starttime += trim
            
            if filter_type is not None and cutoff is not None:
                b, a = butter(N=order, Wn=cutoff, btype=filter_type, fs=fs)
                data = filtfilt(b, a, data)
            
            if normalize:
                max_val = np.max(np.abs(data))
                if max_val > 0:
                    data = data / max_val
            
            new_tr = tr.copy()
            new_tr.data = data
            new_st.append(new_tr)
        
        out_file = output_folder / mseed_file.name
        new_st.write(out_file, format='MSEED')
        print(f"Saved processed file to {out_file}\n")

    return output_folder