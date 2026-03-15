from pathlib import Path
from shutil import copy2
import subprocess
import shutil

def glitcher(raw_folder, channel_folder):

    output_f = Path(r"output_path")
    catalog_f = Path(r"catalog_path")
    input_folder = Path(r"input_path")
    
    folders = [output_f, catalog_f, input_folder]

    for folder in folders:
        for f in folder.glob("*"):
            f.unlink() 

    files_to_copy = Path(channel_folder).glob("*.mseed")
    for f in files_to_copy:
        copy2(f, input_folder)
        
    glitchnet_python = r"glitchnet_path"
    process = subprocess.Popen(
        [glitchnet_python, "detect.py"],
        cwd=r"C:\Users\ben\GlitchNet",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for line in process.stdout:
        print(line, end="")
    process.wait()

    process = subprocess.Popen(
        [glitchnet_python, "deglitch.py"],
        cwd=r"glitchnet_main_path",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for line in process.stdout:
        print(line, end="")
    process.wait()

    channel_folder = Path(channel_folder)
    channel = channel_folder.name
    raw_folder = Path(raw_folder)
    output_p = raw_folder/"deglitched_channels"
    output_p.mkdir(parents=True, exist_ok=True)
    output_folder = output_p/channel
    output_folder.mkdir(parents=True, exist_ok=True)

    
    for f in Path(output_f).glob("*.mseed"):
        new_name = f.name
        if new_name.startswith("deglitched_"):
            new_name = new_name[len("deglitched_"):]
        copy2(f, output_folder / new_name)

    return output_p