# marsquake-signal-phase-analysis
# Seismic signal processing for marsquake phase detection

This repository contains the Python pipeline developed for my Master's Thesis. The goal of the project is to process Mars seismic data from the NASA InSight mission and identify marsquake phases (P and S waves) in high-noise environments.

The workflow includes:
- Automated data downloading and signal preprocessing.
- Application of bandpass filters and noise reduction to clean raw seismic traces.
- Using PhaseNet to predict phase arrivals.
- A validation script that compares automated predictions against manual analyst picks to measure performance.

The code is structured into modules to allow for different filtering parameters to be tested independently. Note that data paths are currently placeholders for portability.
