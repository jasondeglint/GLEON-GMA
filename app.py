# TODO: integrate change, log change and percent change into the same figure
# TODO: enable selection of all years, month range
# TODO: integrate Sam's plots into this
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from data_analysis import DataAnalysis
import re

USEPA_LIMIT = 4
WHO_LIMIT = 20

app = dash.Dash(__name__)

da = DataAnalysis()

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
locations = da.get_locations()

loc_year_plot = da.location_max_avg_yearly()
tn_tp_plot = da.tn_tp_mc()
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
            style={'padding': 10},
            className="six columns"),

        html.Div([
            dcc.Graph(
                id="location-year-scatter",
                figure=loc_year_plot
            ),

            dcc.Dropdown(
                id='loc-dropdown',
                options=[{'label': loc, 'value': loc} for loc in locations],
                value=locations[0]
            )],

            style={'padding': 10},
            className="six columns")

    ], className="row"),
    
    html.Div(
        [
        html.Div([
            html.H2('Data Trends by Lake'),
            dcc.Graph(
                id="temporal-lake-scatter",
                figure=loc_year_plot
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
            )],
            className="twelve columns"
        )],
        className="row"
    ),

    # html.Div(
    #     dcc.Graph(
    #         id="tn_tp_scatter",
    #         figure=tn_tp_plot
    #     ),
    #     style={'padding': 10}
    # ),

    # html.Div(
    #     dcc.RangeSlider(
    #         id="tn_range",
    #         min=0,
    #         max=np.max(df["Total Nitrogen (ug/L)"]),
    #         step=0.5,
    #         value=[0, np.max(df["Total Nitrogen (ug/L)"])],
    #         marks={
    #             1000: '1',
    #             4000: '100',
    #             7000: '1000',
    #             10000: '10000'
    #         },
    #     ),
    #     style={'padding': 10}
    # ),

    # html.Div(
    #     dcc.RangeSlider(
    #         id="tp_range",
    #         min=0,
    #         max=np.max(df["Total Phosphorus (ug/L)"]),
    #         step=0.5,
    #         value=[0, np.max(df["Total Phosphorus (ug/L)"])],
    #         marks={
    #             1000: '1',
    #             4000: '100',
    #             7000: '1000',
    #             10000: '10000'
    #         },
    #     ),
    #     style={'padding': 10}
    # ),
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
        text = df['MC Percent Change'],
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
            text = b1['Microcystin (ug/L)'],
            visible = True,
            name = "MC <= USEPA Limit",
            marker=dict(color="green",opacity = opacity_level)))
    traces.append(go.Scattergeo(
            lon = b2['LONG'],
            lat = b2['LAT'],
            mode = 'markers',
            text = b2['Microcystin (ug/L)'],
            visible = True,
            name = "MC <= WHO Limit",
            marker=dict(color="orange",opacity = opacity_level)))
    traces.append(go.Scattergeo(
            lon = b3['LONG'],
            lat = b3['LAT'],
            mode = 'markers',
            text = b3['Microcystin (ug/L)'],
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

    # if type(selected_years) is not list:
    #     selected_years = [selected_years]
    # if len(selected_years) == 0:
    #     for i in range(len(geo_log_plot.data)):
    #         geo_log_plot.data[i].visible = False
    # else:
    #     min_index = years.index(min(selected_years)) * 12 + month
    #     max_index = years.index(max(selected_years)) * 12 + month
    #     if min_index == max_index:
    #         max_index += 1
    #     for i in range(len(geo_log_plot.data)):
    #         geo_log_plot.data[i].visible = i in range(min_index, max_index)
    # return geo_log_plot

@app.callback(
    dash.dependencies.Output('temporal-lake-scatter', 'figure'),
    [dash.dependencies.Input('temporal-lake-col', 'value'),
     dash.dependencies.Input('temporal-lake-location', 'value')])
def temporal_lake(selected_col, selected_loc):
    selected_col_stripped = re.sub("[\(\[].*?[\)\]]", "", selected_col)
    selected_col_stripped = re.sub('\s+', ' ', selected_col_stripped).strip()
    selected_data = df[df['Body of Water Name'] == selected_loc]
    x_data=pd.to_datetime(selected_data['DATETIME'])
    y_data=selected_data[selected_col]

    data = go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines',
        marker={
           'opacity': 0.8,
        },
        line = {
            'width': 1.5
        }
    )
    layout = go.Layout(
        title= '%s Trends for %s' %(selected_col_stripped, " ".join(w.capitalize() for w in selected_loc.split())), 
        xaxis={'title':'Date'},
        yaxis={'title': str(selected_col)}
    )
    temporal_lake_plot = {
        'data': [data],
        'layout': layout
    } 
    return temporal_lake_plot

# @app.callback(
#     dash.dependencies.Output('location-year-scatter', 'figure'),
#     [dash.dependencies.Input('loc-dropdown', 'value')])
# def update_loc_graph(location):
#     for i in range(len(geo_log_plot.data)):
#         loc_year_plot.data[i].visible = i == locations.index(location) or i == locations.index(location) + 1
#     return loc_year_plot

# @app.callback(
#     dash.dependencies.Output('tn_tp_scatter', 'figure'),
#     [dash.dependencies.Input('tn_range', 'value'),
#      dash.dependencies.Input('tp_range', 'value'),])
# def update_output(tn_val, tp_val):
#     return da.tn_tp_mc(tn_val[0],tn_val[1], tp_val[0],tp_val[1])

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True)
