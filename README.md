# GLEON-GMA

## Overview

The project homepage can be found here:

http://gleon.org/research/projects/global-microcystin-aggregation-gma


The google doc can be found at this link. Everyone who has this link has edit privileges:

https://docs.google.com/document/d/1cBisJHwE5sdh0tUYPaePRuaECr24Lif8l7mhDZnvTTQ/edit?usp=sharing


GLEON summary page:

https://docs.google.com/document/d/1M-wcmNoGbqPsOTJK8EGxzJxdAKEDN3WWqqxAne5mCZI/edit

## Setup Environment

This project requires Python 3. Please refer to the instructions for installing Python 3 and setting the path variable on your system:
https://www.python.org/downloads/

Git is required to clone the repository. Please refer to the instructions for downloading for your operating system here: https://git-scm.com/downloads

Also ensure that the pipenv has been installed. To install pipenv, run:

```
pip install pipenv  " replace pip with pip3 or the appropriate environment variable
```

If pip is not installed, follow the instructions here: https://pip.pypa.io/en/stable/installing/

### Installing Anaconda - Running jupyter notebook

Please refer to installation instructions to download Anaconda for running jupyter notebook:
https://docs.anaconda.com/anaconda/install/

To test the installation and run jupyter notebook, run the following command
```
jupyter notebook
```

In order to run display plotly plots in the jupyter notebook, run:
jupyter labextension install @jupyterlab/plotly-extension
Note: nodejs and npm also need to be installed on the system


### Dash Application

![](cap.gif)


To run the DASH application, run the following commands
```
git clone https://github.com/jasondeglint/GLEON-GMA/
cd GLEON-GMA
python -m pipenv install
cd dash
python -m pipenv run app.py
```
Instead of the last command to run "app.py" the following command can be used as well
```
pipenv run python app.py
```

### Next Steps
1. Adding instructions to use sample database file
2. Publish website to VPS to go live and begin taking in dataset files
3. Add correlation matrix graph (Michael)
4. Add field method column, search bar to the metadata table
5. Auto add continent as a column in the spreadsheet (similar to how we make DB IDs)
6. More information hover ability in metadata table to show information not provided in table (ex: institution, if sample was filtered)
7. Differentiate lakes if same lake, different lat/long (ex: Alligator Lake (40, 50) vs Alligator Lake (41, 51))

### Known Issues
1. Some newly uploaded datasets have a problem when updating in updating_dataframe in db_engine.py, dataframe column dividing throws an exception
2. Alligator Lake in the Bigham dataset has a strange trend pattern due to samples being taken from different locations on the lake
3. When Graphs are loaded, geographical graph will not show dots. Requires a selected year to be removed for the graph to update (may publish map before the options are selected upon loading)
