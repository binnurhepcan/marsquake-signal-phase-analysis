import subprocess
import csv
import os
from pathlib import Path
from obspy import read, Stream

def to_wsl_path(win_path):
    path = Path(win_path).resolve()
    drive = path.drive.lower().replace(":", "")
    rest = str(path).replace("\\", "/").split(":/")[-1]
    rest = rest.lstrip("/") 
    return f"/mnt/{drive}/{rest}"

def run_phasenet_wsl(input_path):
    
    input_dir = Path(input_path).resolve()
    output_dir = (input_dir/"result").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = input_dir / "mseed.csv"
    mseed_files = sorted(input_dir.glob("*.mseed"))

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fname"])
        for fpath in mseed_files:
            writer.writerow([fpath.name])

    first_mseed = next(input_dir.glob("*.mseed"), None)
    st = read(first_mseed)
    sampling_rate = st[0].stats.sampling_rate
    
    wsl_input = to_wsl_path(input_dir)
    wsl_output = to_wsl_path(output_dir)
    wsl_csv = to_wsl_path(csv_path)

    command = (
        f'wsl -d Ubuntu -e bash -ic "conda activate phasenet39 && '
        f'cd ~/PhaseNet && '
        f'python phasenet/predict.py '
        f'--model=model/190703-214543 '
        f'--data_list={wsl_csv} '
        f'--data_dir={wsl_input} '
        f'--format=mseed '
        f'--amplitude '
        f'--batch_size=1 '
        f'--sampling_rate={sampling_rate} '
        f'--result_dir={wsl_output}"'
    )

    print(f"Running: {command}\n")

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8", 
        errors="replace",
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="", flush=True) 

    process.wait()
    print(f"PhaseNet finished!!!!! Results saved in: {output_dir}")

    return input_dir, output_dir