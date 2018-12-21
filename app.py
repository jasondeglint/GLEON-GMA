import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import data_analysis as da
from settings import df, months, cols, year, years, locations, USEPA_LIMIT, WHO_LIMIT 

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='GLEON MC Data Analysis'),

        html.Div([
            html.H2('Microcystin Concentration'),
            dcc.Graph(id='geo_plot'),
            dcc.RadioItems(
                id="geo_plot_option",
                options=[{'label': 'Show Concentration Plot', 'value': 'CONC'},
                        {'label': 'Show Log Concentration Change Plot', 'value': 'LOG'}],
                        value='CONC'),
            html.Div([
                html.Div(html.P("Year:")),
                html.Div(
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=[{'label': str(y), 'value': y} for y in years],
                        multi=True,
                        value=np.min(year)
                    ),
                ),
            ]),
            html.Div([
                    html.P("Month:"),
                    dcc.Slider(
                        id='month-slider',
                        min=0,
                        max=11,
                        value=1,
                        marks={i: months[i] for i in range(len(months))}
                )]),
            ],
            style={'padding': 10},
            className="row"
    ),
    
    html.H2('Total Phosphorus vs Total Nitrogen'),
    html.Div(
        dcc.Graph(
            id="tn_tp_scatter",
        ),
        style={'padding': 10},
        className="row"
    ),

    html.Div([
        html.P("Log TN:"),
        dcc.RangeSlider(
            id="tn_range",
            min=0,
            max=np.max(df["Total Nitrogen (ug/L)"]),
            step=0.5,
            value=[0, np.max(df["Total Nitrogen (ug/L)"])],
            marks={
                1000: '1',
                4000: '100',
                7000: '1000',
                10000: '10000'
            },
        ),
    ],
        style={'padding': 10},
        className="row"
    ),

    html.Div([
        html.P("Log TP:"),
        dcc.RangeSlider(
            id="tp_range",
            min=0,
            max=np.max(df["Total Phosphorus (ug/L)"]),
            step=0.5,
            value=[0, np.max(df["Total Phosphorus (ug/L)"])],
            marks={
                1000: '1',
                4000: '100',
                7000: '1000',
                10000: '10000'
            },
        ),
    ],
        style={'padding': 10},
        className="row"
    ),
    
    html.Div([
        html.H2('Data Trends by Lake'),
        dcc.Graph(
            id="temporal-lake-scatter",
        ),

        dcc.Dropdown(
            id="temporal-lake-col",
            options=[{'label': c, 'value': c} for c in cols],
            value=cols[0],
            style={'margin-top': 10, 'z-index': 10},
            className='six columns'
        ),
        dcc.Dropdown(
            id='temporal-lake-location',
            options=[{'label': loc, 'value': loc} for loc in locations],
            value=locations[0],
            style={'margin-top': 10},
            className='six columns'
        )
    ],
        style={'padding': 10},
        className="row"
    ),
])

@app.callback(
    dash.dependencies.Output('geo_plot', 'figure'),
    [dash.dependencies.Input('year-dropdown', 'value'),
     dash.dependencies.Input('month-slider', 'value'),
     dash.dependencies.Input('geo_plot_option','value')])
def update_geo_plot(selected_years, selected_month, geo_option):
    return da.geo_plot(selected_years, selected_month, geo_option)

@app.callback(
    dash.dependencies.Output('temporal-lake-scatter', 'figure'),
    [dash.dependencies.Input('temporal-lake-col', 'value'),
     dash.dependencies.Input('temporal-lake-location', 'value')])
def update_output(selected_col, selected_loc):
    return da.temporal_lake(selected_col, selected_loc)

@app.callback(
    dash.dependencies.Output('tn_tp_scatter', 'figure'),
    [dash.dependencies.Input('tn_range', 'value'),
     dash.dependencies.Input('tp_range', 'value'),])
def update_output(tn_val, tp_val):
    return da.tn_tp(tn_val, tp_val)

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True)
