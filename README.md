# GLEON-GMA

The project homepage can be found here:

http://gleon.org/research/projects/global-microcystin-aggregation-gma


The google doc can be found at this link. Everyone who has this link has edit privileges:

https://docs.google.com/document/d/1cBisJHwE5sdh0tUYPaePRuaECr24Lif8l7mhDZnvTTQ/edit?usp=sharing


In order to run display plotly plots in the jupyter notebook, run:
jupyter labextension install @jupyterlab/plotly-extension
Note: nodejs and npm also need to be installed on the system


### Dash Application

![](cap.gif)


This project requires Python 3. Please refer to the instructions for installing Python 3 and setting the path variable on your system:
https://www.python.org/downloads/

Also ensure that the pipenv has been installed. To install pipenv, run:

```
pip install pipenv  " replace pip with pip3 or the appropriate environment variable
```

To run the DASH application, run the following commands
```
git clone https://github.com/jasondeglint/GLEON-GMA/
cd GLEON-GMA
python -m pipenv install
python -m pipenv run app.py
```

### Next Steps
1. Incorpoprate additional data into analysis.
