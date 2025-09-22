import subprocess
from pathlib import Path

def run_dust_pre(folder_path: str) -> None:
    """Run dust_pre in the given folder."""
    folder = Path(folder_path)
    subprocess.run(["dust_pre"], cwd=folder, check=True)

def run_dust(folder_path: str) -> None:
    """Run dust in the given folder."""
    folder = Path(folder_path)
    subprocess.run(["dust"], cwd=folder, check=True)

def run_dust_post(folder_path: str) -> None:
    """Run dust_post in the given folder."""
    folder = Path(folder_path)
    subprocess.run(["dust_post"], cwd=folder, check=True)

def run_full_simulation(folder_path: str) -> None:
    """Run preprocessing, simulation, and postprocessing in sequence."""
    run_dust_pre(folder_path)
    run_dust(folder_path)
    run_dust_post(folder_path)
