# Project: Analysing-Sensitive-Speech

# Introduction 
The objective of this project is to analyze sensitive speech in social media, as well as its contagion.

# Documentation

## Code Organization

The code is set up into several main directories:
- [**data**](https://github.com/Yocodeyo/Analysing-Sensitive-Speech/tree/main/data): contains the data to be used for model training and dashboarding
  - [**hashed__0_data**](https://github.com/Yocodeyo/Analysing-Sensitive-Speech/blob/main/data/hashed_0_data.h5): Raw data provided by the client
  - [**time_elapsed.csv**](https://github.com/Yocodeyo/Analysing-Sensitive-Speech/blob/main/data/time_elapsed.csv): Processed data with cleaned post_dates
- [**assets**](https://github.com/Yocodeyo/Analysing-Sensitive-Speech/tree/main/assets): Contains css stylesheets for the dashboard
- Are we including our models and notebooks in here too?

## Data Processing
[**graph_data_cleaning.py**](https://github.com/Yocodeyo/Analysing-Sensitive-Speech/blob/main/graph_data_cleaning.py) is a script for generating time_elapsed.csv, and can be executed in the command line using ```python graph_data_cleaning.py```


