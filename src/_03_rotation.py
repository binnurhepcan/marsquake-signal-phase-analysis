from obspy import read, Stream
from pathlib import Path
import numpy as np
from obspy.signal.rotate import rotate2zne

def rotation(rotation_file_path):

    input_folder = Path(rotation_file_path)
    output_folder = input_folder / "rotated"
    output_folder.mkdir(exist_ok=True)
    
    az_u, dip_u = 135.1, -29.4
    az_v, dip_v = 15.0, -29.2
    az_w, dip_w = 255.0, -29.7

    for mseed_path in input_folder.glob("*.mseed"):

        st = read(mseed_path)
        
        min_npts = min(tr.stats.npts for tr in st)
        
        for tr in st:
            tr.trim(starttime=tr.stats.starttime, endtime=tr.stats.starttime + (min_npts-1)/tr.stats.sampling_rate)
            #print(tr.id, tr.stats.npts)

        components = [tr.stats.channel[-1] for tr in st]  # last letter of each trace
        if not all(k in components for k in ("U", "V", "W")):
            print(f"Skipping {mseed_path.name}: missing components")
            continue
            
        u = st.select(component="U")[0].data
        v = st.select(component="V")[0].data
        w = st.select(component="W")[0].data
        
        z, n, e = rotate2zne(
            u, az_u, dip_u,
            v, az_v, dip_v,
            w, az_w, dip_w,
            inverse=False
        )
    
        tr_z = st.select(component="U")[0].copy()
        tr_n = st.select(component="V")[0].copy()
        tr_e = st.select(component="W")[0].copy()
    
        tr_z.data = z.astype(np.float32)
        tr_n.data = n.astype(np.float32)
        tr_e.data = e.astype(np.float32)

        for arr, tr in zip([z, n, e], [tr_z, tr_n, tr_e]):
            tr.data = np.asarray(arr, dtype=np.float32)
            tr.stats.mseed.encoding = "FLOAT32"
    
        tr_z.stats.channel = tr_z.stats.channel[:-1] + "Z"
        tr_n.stats.channel = tr_n.stats.channel[:-1] + "N"
        tr_e.stats.channel = tr_e.stats.channel[:-1] + "E"
    
        rotated_st = Stream([tr_z, tr_n, tr_e])
        
        output_path = output_folder / (mseed_path.stem + ".mseed")
        rotated_st.write(output_path, format="MSEED")

    return output_folder