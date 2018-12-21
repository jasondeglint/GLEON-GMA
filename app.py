import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import re

USEPA_LIMIT = 4
WHO_LIMIT = 20

app = dash.Dash(__name__)

alberta = pd.read_pickle("data/alberta.pkl")
florida = pd.read_pickle("data/florida.pkl")
df = pd.concat([alberta, florida], sort=False).reset_index(drop=True)

df["TN:TP"] = df["Total Nitrogen (ug/L)"]/df["Total Phosphorus (ug/L)"]

df["MC Percent Change"] = df.sort_values("DATETIME").\
                groupby(['LONG','LAT'])["Microcystin (ug/L)"].\
                apply(lambda x: x.pct_change()).fillna(0)

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
cols = ['Microcystin (ug/L)', 'Total Nitrogen (ug/L)', 'Total Phosphorus (ug/L)', 'Secchi Depth (m)', 'Total Chlorophyll (ug/L)', 'Temperature (degrees celsius)']
year = pd.to_datetime(df['DATETIME']).dt.year
years = range(np.min(year), np.max(year)+1)

# temporal_lake_plot = da.temporal_lake()

app.layout = html.Div(children=[
    html.H1(children='GLEON MC Data Analysis'),

    html.Div([
        html.Div([
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
            style={'padding': 10}),

    ], className="row"),
    
    html.Div(
        [
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
            )],
            className="twelve columns"
        )],
        className="row"
    ),

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
])

@app.callback(
    dash.dependencies.Output('geo_plot', 'figure'),
    [dash.dependencies.Input('year-dropdown', 'value'),
     dash.dependencies.Input('month-slider', 'value'),
     dash.dependencies.Input('geo_plot_option','value')])
def update_geo_plot(selected_years, selected_month, geo_option):
    if type(selected_years) is not list:
        selected_years = [selected_years]

    month = pd.to_datetime(df['DATETIME']).dt.month
    year = pd.to_datetime(df['DATETIME']).dt.year
    selected_data = df[(month == selected_month) & (year.isin(selected_years))]
    if geo_option == "CONC":
        return geo_concentration_plot(selected_data)
    else:
        return geo_log_plot(selected_data)


def geo_log_plot(selected_data):
    selected_data["MC_pc_bin"] = np.log(np.abs(selected_data["MC Percent Change"]) + 1)
    data = [go.Scattergeo(
        lon = selected_data['LONG'],
        lat = selected_data['LAT'],
        mode = 'markers',
        text = df["Body of Water Name"],
        visible = True,
        #name = "MC > WHO Limit",
        marker = dict(
            size = 6,
            reversescale = True,
            autocolorscale = False,
            symbol = 'circle',
            opacity = 0.6,
            line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale = 'Viridis' ,
            cmin = 0,
            color = selected_data['MC_pc_bin'],
            cmax = selected_data['MC_pc_bin'].max(),
            colorbar=dict(
                title="Value")

    ))]

    layout = go.Layout(title='Log Microcystin Concentration Change',
                        showlegend=False,
                        geo = dict(
                                scope='north america',
                                showframe = False,
                                showcoastlines = True,
                                showlakes = True,
                                showland = True,
                                landcolor = "rgb(229, 229, 229)",
                                showrivers = True
                            ))

    fig = go.Figure(layout=layout, data=data)    
    return fig

def geo_concentration_plot(selected_data):
    traces = []
    opacity_level = 0.8
    MC_conc = selected_data['Microcystin (ug/L)']
    # make bins
    b1 = selected_data[MC_conc <= USEPA_LIMIT]
    b2 = selected_data[(MC_conc > USEPA_LIMIT) & (MC_conc <= WHO_LIMIT)]
    b3 = selected_data[MC_conc > WHO_LIMIT]
    traces.append(go.Scattergeo(
            lon = b1['LONG'],
            lat = b1['LAT'],
            mode = 'markers',
            text = b1["Body of Water Name"],
            visible = True,
            name = "MC <= USEPA Limit",
            marker=dict(color="green",opacity = opacity_level)))
    traces.append(go.Scattergeo(
            lon = b2['LONG'],
            lat = b2['LAT'],
            mode = 'markers',
            text = b2["Body of Water Name"],
            visible = True,
            name = "MC <= WHO Limit",
            marker=dict(color="orange",opacity = opacity_level)))
    traces.append(go.Scattergeo(
            lon = b3['LONG'],
            lat = b3['LAT'],
            mode = 'markers',
            text = b3["Body of Water Name"],
            visible = True,
            name = "MC > WHO Limit",
            marker=dict(color="red",opacity = opacity_level)))
    
       
    layout = go.Layout(showlegend=True,
                        title="Microcystin Concentration",
                        geo = dict(
                                scope='north america',
                                showframe = True,
                                showcoastlines = True,
                                showlakes = True,
                                showland = True,
                                landcolor = "rgb(229, 229, 229)",
                                showrivers = True
                            ))

    fig = go.Figure(layout=layout, data=traces)  
    return fig

@app.callback(
    dash.dependencies.Output('temporal-lake-scatter', 'figure'),
    [dash.dependencies.Input('temporal-lake-col', 'value'),
     dash.dependencies.Input('geo_plot', 'selectedData')])
def temporal_lake(selected_col, selected_points):

    if selected_points is None:
        return go.Figure()

    selected_col_stripped = re.sub("[\(\[].*?[\)\]]", "", selected_col)
    selected_col_stripped = re.sub('\s+', ' ', selected_col_stripped).strip()
 
    locations = [point['text'] for point in selected_points["points"]] 
    selected_data = df[df["Body of Water Name"].isin(locations)]
    groups = selected_data.groupby("Body of Water Name")
    traces = []
    for name, group in groups:
        x_data=pd.to_datetime(group['DATETIME'])
        y_data=group[selected_col]

        traces.append(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            name =f'{name}',
            marker={
            'opacity': 0.8,
            },
            line = {
                'width': 1.5
            }
        ))
    layout = go.Layout(
        title= '%s Trends' % (selected_col_stripped), 
        xaxis={'title':'Date'},
        yaxis={'title': str(selected_col)}
    )

    temporal_lake_plot = {
        'data': traces,
        'layout': layout
    } 
    return temporal_lake_plot

@app.callback(
    dash.dependencies.Output('tn_tp_scatter', 'figure'),
    [dash.dependencies.Input('tn_range', 'value'),
     dash.dependencies.Input('tp_range', 'value'),])
def update_output(tn_val, tp_val):
    min_tn = tn_val[0]
    max_tn = tn_val[1]
    min_tp = tp_val[0]
    max_tp = tp_val[1]

    if max_tn == 0:
        max_tn = np.max(df["Total Nitrogen (ug/L)"])

    if max_tp == 0:
        max_tp = np.max(df["Total Phosphorus (ug/L)"])

    dat = df[(df["Total Nitrogen (ug/L)"] >= min_tn) & (df["Total Nitrogen (ug/L)"] <= max_tn) & (df["Total Phosphorus (ug/L)"] >= min_tp) & (df["Total Phosphorus (ug/L)"] <= max_tp)]
    MC_conc = dat['Microcystin (ug/L)']
    # make bins
    b1 = dat[MC_conc <= USEPA_LIMIT]
    b2 = dat[(MC_conc > USEPA_LIMIT) & (MC_conc <= WHO_LIMIT)]
    b3 = dat[MC_conc > WHO_LIMIT]

    data = [go.Scatter(
        x=np.log(b1["Total Nitrogen (ug/L)"]),
        y=np.log(b1["Total Phosphorus (ug/L)"]),
        mode = 'markers',
        name="<USEPA",
        marker=dict(
            size=8,
            color = "green", #set color equal to a variable
        )),
        go.Scatter(
        x=np.log(b2["Total Nitrogen (ug/L)"]),
        y=np.log(b2["Total Phosphorus (ug/L)"]),
        mode = 'markers',
        name=">USEPA",
        marker=dict(
            size=8,
            color = "orange" #set color equal to a variable
        )),
        go.Scatter(
        x=np.log(b3["Total Nitrogen (ug/L)"]),
        y=np.log(b3["Total Phosphorus (ug/L)"]),
        mode = 'markers',
        name=">WHO",
        marker=dict(
            size=8,
            color = "red", #set color equal to a variable
        ))]

    layout = go.Layout(
        showlegend=True,
        xaxis=dict(
            title='log TN'),
        yaxis=dict(
            title="log TP")
        )

    return (go.Figure(data=data, layout=layout))


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True)
