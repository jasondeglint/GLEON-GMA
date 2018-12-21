import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import re
from settings import df, months, cols, year, years, locations, USEPA_LIMIT, WHO_LIMIT 

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

def geo_plot(selected_years, selected_month, geo_option):
    if type(selected_years) is not list:
        selected_years = [selected_years]

    month = pd.to_datetime(df['DATETIME']).dt.month
    year = pd.to_datetime(df['DATETIME']).dt.year
    selected_data = df[(month == selected_month) & (year.isin(selected_years))]
    if geo_option == "CONC":
        return geo_concentration_plot(selected_data)
    else:
        return geo_log_plot(selected_data)

def tn_tp(tn_val, tp_val):
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
        title= '%s Trends' % (selected_col_stripped), 
        xaxis={'title':'Date'},
        yaxis={'title': str(selected_col)}
    )

    temporal_lake_plot = {
        'data': [data],
        'layout': layout
    } 
    return temporal_lake_plot
