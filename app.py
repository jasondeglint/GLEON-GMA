import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from data_analysis import DataAnalysis

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

da = DataAnalysis()
df = da.get_df()

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
year = pd.to_datetime(df['DATETIME']).dt.year
years = range(np.min(year), np.max(year)+1)

geo_conc_plot = da.geo_concentration_plot()
geo_log_plot = da.log_change_plot()

app.layout = html.Div(children=[
    html.H1(children='Spatial MC conc'),

    dcc.Graph(
         id='geo_conc_plot',
         figure=geo_conc_plot
    ),

    dcc.Graph(
         id='geo_log_plot',
         figure=geo_log_plot
    ),

    html.Div(
        dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(y), 'value': y} for y in years],
        value=np.min(year)
    )),

    html.Div(
        dcc.Slider(
            id='month-slider',
            min=0,
            max=11,
            value=1,
            marks={i: months[i] for i in range(len(months))}
    ))
])

@app.callback(
    dash.dependencies.Output('geo_log_plot', 'figure'),
    [dash.dependencies.Input('year-dropdown', 'value'),
     dash.dependencies.Input('month-slider', 'value')])
def update_graph(year, month):
    for i in range(len(geo_log_plot.data)):
        geo_log_plot.data[i].visible = i == years.index(year) * 12 + month
    return geo_log_plot

if __name__ == '__main__':
    app.run_server(debug=True)
