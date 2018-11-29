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
locations = da.get_locations()

geo_conc_plot = da.geo_concentration_plot()
geo_log_plot = da.log_change_plot()
loc_year_plot = da.location_max_avg_yearly()
tn_tp_plot = da.tn_tp_mc()

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
    ),
        style={'padding': 10}
    ),

    html.Div(
        dcc.Slider(
            id='month-slider',
            min=0,
            max=11,
            value=1,
            marks={i: months[i] for i in range(len(months))}
    ),
        style={'padding': 10}
    ),

    html.Div(
        dcc.Graph(
            id="location-year-scatter",
            figure=loc_year_plot
        ),
        style={'padding': 10}
    ),

    html.Div(
        dcc.Dropdown(
        id='loc-dropdown',
        options=[{'label': loc, 'value': loc} for loc in locations],
        value=locations[0]),
        style={'padding': 10}
    ),

    html.Div(
        dcc.Graph(
            id="tn_tp_scatter",
            figure=tn_tp_plot
        ),
        style={'padding': 10}
    ),

    html.Div(
        dcc.RangeSlider(
            id="tn_tp_range",
            min=0,
            max=np.max(df["TN:TP"]),
            step=0.5,
            value=[0,100]
        ),
        style={'padding': 10}
    ),
])

@app.callback(
    dash.dependencies.Output('geo_log_plot', 'figure'),
    [dash.dependencies.Input('year-dropdown', 'value'),
     dash.dependencies.Input('month-slider', 'value')])
def update_log_graph(year, month):
    for i in range(len(geo_log_plot.data)):
        geo_log_plot.data[i].visible = i == years.index(year) * 12 + month
    return geo_log_plot

@app.callback(
    dash.dependencies.Output('location-year-scatter', 'figure'),
    [dash.dependencies.Input('loc-dropdown', 'value')])
def update_loc_graph(location):
    for i in range(len(geo_log_plot.data)):
        loc_year_plot.data[i].visible = i == locations.index(location) or i == locations.index(location) + 1
    return loc_year_plot

@app.callback(
    dash.dependencies.Output('tn_tp_scatter', 'figure'),
    [dash.dependencies.Input('tn_tp_range', 'value')])
def update_output(value):
    return da.tn_tp_mc(value[0],value[1])


if __name__ == '__main__':
    app.run_server(debug=True)
