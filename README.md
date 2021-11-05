# Project: Analysing-Sensitive-Speech

# Introduction 
The objective of this project is to analyze sensitive speech in social media, as well as its contagion.

# Usage Instructions
Please have **Python** installed on your device. You can create a `conda` environment if you have Anaconda installed on your device.
1. Open Command Line Terminal
2. Type: `git clone https://github.com/Yocodeyo/Analysing-Sensitive-Speech` (download our code)
3. Type: `cd Analysing-Sensitive-Speech` (go to the folder you just downloaded)
4. Type: `pip install -r requirements.txt` (set up relevant libraries for use)
5. Type: `python index.py` (run the dashboard)
6. Open http://127.0.0.1:8050/ in your browser to visualise the dashboard.

# Documentation

## Code Organization

The code is set up into several main directories:
- [**apps**](https://github.com/Yocodeyo/Analysing-Sensitive-Speech/tree/main/apps): Stores the graphs to be imported into the dashboard
- [**assets**](https://github.com/Yocodeyo/Analysing-Sensitive-Speech/tree/main/assets): Stores CSS stylesheets
- [**outputs**](https://github.com/Yocodeyo/Analysing-Sensitive-Speech/tree/main/outputs): Stores the input data for the graphs
     - The input data for each graph is stored in a sub-folder corresponding to its name
     - hashed_0_data.h5 is the hashed source file provided by the client



