import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import data_analysis as da
from settings import df, months, years, cols, locations

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div([
        html.H1(children='GLEON MC Data Analysis')
    ], className="title"),

    html.Div([
        html.H2('Microcystin Concentration'),
        dcc.Graph(id='geo_plot'),
        html.Div([
            dcc.RadioItems(
            id="geo_plot_option",
            options=[{'label': 'Show Concentration Plot', 'value': 'CONC'},
                    {'label': 'Show Log Concentration Change Plot', 'value': 'LOG'}],
                    value='CONC'),
        ]),
        html.Div([
            html.Div(html.P("Year:")),
            html.Div(
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': str(y), 'value': y} for y in years],
                    multi=True,
                    value=np.min(years)
                ),
            )
        ]),
        html.Div([
            html.P("Month:"),
            dcc.Slider(
                id='month-slider',
                min=0,
                max=11,
                value=1,
                marks={i: months[i] for i in range(len(months))}
            )
        ]),
    ], className="row"),
    
    html.Div([
        html.H2('Total Phosphorus vs Total Nitrogen'),

        dcc.Graph(
            id="tn_tp_scatter",
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
        ]),

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
        ]),
    ], className="row"),
    
    html.Div([
        html.H2('Data Trends by Lake'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id="temporal-lake-scatter",
                )
            ], className='six columns'),
            html.Div([
                dcc.Graph(
                    id="temporal-lake-pc-scatter",
                )
            ], className='six columns'),
        ]),
        dcc.Dropdown(
            id="temporal-lake-col",
            options=[{'label': c, 'value': c} for c in cols],
            value=cols[0],
            className='six columns'
        ),
        dcc.Dropdown(
            id='temporal-lake-location',
            options=[{'label': loc, 'value': loc} for loc in locations],
            value=locations[0],
            className='six columns'
        )
    ], className="row"),
    
    html.Div([
        html.H2('Overall Temporal Data Trends'),
        html.P('Includes data from all lakes'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id="temporal-avg-scatter",
                )
            ], className='six columns'),
            html.Div([
                dcc.Graph(
                    id="temporal-pc-scatter",
                )
            ], className='six columns'),
        ]),
        dcc.Dropdown(
            id="temporal-avg-col",
            options=[{'label': c, 'value': c} for c in cols],
            value=cols[0]
        )
    ], className='row'),
    
    html.Div([
        html.H2('Raw Data'),
        dcc.Graph(
            id="temporal-raw-scatter",
        ),
        html.Div([
            html.Div([
                dcc.RadioItems(
                    id="temporal-raw-option",
                    options=[{'label': 'Show All Raw Data', 'value': 'RAW'},
                            {'label': 'Show Data Within 3 Standard Deviations', 'value': '3SD'}],
                            value='RAW'
                )
            ], className='six columns'),
            html.Div([
                dcc.Dropdown(
                    id="temporal-raw-col",
                    options=[{'label': c, 'value': c} for c in cols],
                    value=cols[0]
                )
            ], className='six columns')
        ])
    ], className='row')
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
    return da.temporal_lake(selected_col, selected_loc, 'raw')

@app.callback(
    dash.dependencies.Output('temporal-lake-pc-scatter', 'figure'),
    [dash.dependencies.Input('temporal-lake-col', 'value'),
     dash.dependencies.Input('temporal-lake-location', 'value')])
def update_output(selected_col, selected_loc):
    return da.temporal_lake(selected_col, selected_loc, 'pc')

@app.callback(
    dash.dependencies.Output('tn_tp_scatter', 'figure'),
    [dash.dependencies.Input('tn_range', 'value'),
     dash.dependencies.Input('tp_range', 'value'),])
def update_output(tn_val, tp_val):
    return da.tn_tp(tn_val, tp_val)

@app.callback(
    dash.dependencies.Output('temporal-avg-scatter', 'figure'),
    [dash.dependencies.Input('temporal-avg-col', 'value')])
def update_output(selected_col):
    return da.temporal_overall(selected_col, 'avg')

@app.callback(
    dash.dependencies.Output('temporal-pc-scatter', 'figure'),
    [dash.dependencies.Input('temporal-avg-col', 'value')])
def update_output(selected_col):
    return da.temporal_overall(selected_col, 'pc')

@app.callback(
    dash.dependencies.Output('temporal-raw-scatter', 'figure'),
    [dash.dependencies.Input('temporal-raw-option', 'value'),
     dash.dependencies.Input('temporal-raw-col', 'value'),])
def update_output(selected_option, selected_col):
    return da.temporal_raw(selected_option, selected_col)

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True)
