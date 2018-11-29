import pandas as pd
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np

class DataAnalysis:
    def __init__(self):

        # def get_category(conc):

        #     USEPA_LIMIT = 4
        #     WHO_LIMIT = 20
        #     if conc < USEPA_LIMIT:
        #         return "<USEPA"
        #     elif conc <= WHO_LIMIT:
        #         return "<WHO"
        #     else:
        #         return ">WHO"

                
        alberta = pd.read_pickle("data/alberta.pkl")
        florida = pd.read_pickle("data/florida.pkl")
        self.df = pd.concat([alberta, florida], sort=False).reset_index(drop=True)

        self.df["TN:TP"] = self.df["Total Nitrogen (ug/L)"]/self.df["Total Phosphorus (ug/L)"]

        # self.df["conc_cat"] = self.df["Microcystin (ug/L)"].apply(get_category)

        self.df["MC Percent Change"] = self.df.sort_values("DATETIME").\
                            groupby(['LONG','LAT'])["Microcystin (ug/L)"].\
                            apply(lambda x: x.pct_change()).fillna(0)

        

    def geo_concentration_plot(self):
        '''
        Returns a figure of the geospatial plot, color coded according to guideline limits
        '''

        USEPA_LIMIT = 4
        WHO_LIMIT = 20

        MC_level = self.df['Microcystin (ug/L)']
        opacity_level = 0.8

        month = pd.to_datetime(self.df['DATETIME']).dt.month

        traces = []
        for m in range(1,13):
            month_data = self.df[month == m]
            MC_conc = month_data['Microcystin (ug/L)']
            # make bins
            b1 = month_data[MC_conc <= USEPA_LIMIT]
            b2 = month_data[(MC_conc > USEPA_LIMIT) & (MC_conc <= WHO_LIMIT)]
            b3 = month_data[MC_conc > WHO_LIMIT]
            traces.append(go.Scattergeo(
                    lon = b1['LONG'],
                    lat = b1['LAT'],
                    mode = 'markers',
                    text = b1['Microcystin (ug/L)'],
                    visible = False,
                    name = "MC <= USEPA Limit",
                    marker=dict(color="green",opacity = opacity_level)))
            traces.append(go.Scattergeo(
                    lon = b2['LONG'],
                    lat = b2['LAT'],
                    mode = 'markers',
                    text = b2['Microcystin (ug/L)'],
                    visible = False,
                    name = "MC <= WHO Limit",
                    marker=dict(color="orange",opacity = opacity_level)))
            traces.append(go.Scattergeo(
                    lon = b3['LONG'],
                    lat = b3['LAT'],
                    mode = 'markers',
                    text = b3['Microcystin (ug/L)'],
                    visible = False,
                    name = "MC > WHO Limit",
                    marker=dict(color="red",opacity = opacity_level)))
            
        steps = []
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            
        for i in range(12):
            step = dict(
            method = 'restyle',  
            args = ['visible', [False] * len(traces)],
            label= months[i])
            
            idx1 = (i+1) * 3 - 3
            idx2 = (i+1) * 3 - 2
            idx3 = (i+1) * 3 - 1
            
            step['args'][1][idx1] = True
            step['args'][1][idx2] = True
            step['args'][1][idx3] = True
            
            steps.append(step)
            
        sliders = [dict(
            active = 0,
            steps=steps
        )]

        # Display all traces pertaining to the month of January
        traces[0].visible = True
        traces[1].visible = True
        traces[2].visible = True

        layout = go.Layout(title='Microcystin concentration',
                        showlegend=True,
                        sliders = sliders,
                            geo = dict(
                                    scope='north america',
                                    showframe = False,
                                    showcoastlines = True,
                                    showlakes = True,
                                    showland = True,
                                    landcolor = "rgb(229, 229, 229)",
                                    showrivers = True
                                ))

        fig = go.Figure(layout=layout, data=traces)  
        return fig

    def log_change_plot(self):
        '''
        Returns the loc MC change plot
        '''

        month = pd.to_datetime(self.df['DATETIME']).dt.month
        #df["MC_pc_bin"] = np.log(df["MC percent change"])

        traces = []
        year = pd.to_datetime(self.df['DATETIME']).dt.year
        years = range(np.min(year), np.max(year)+1)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        ################ Add info about traces
        for y in years:
            for m in range(len(months)):
                time_data = self.df[(month == m) & (year == y)]
                time_data["MC_pc_bin"] = np.log(np.abs(time_data["MC Percent Change"]) + 1)
                traces.append(go.Scattergeo(
                        lon = time_data['LONG'],
                        lat = time_data['LAT'],
                        mode = 'markers',
                        text = self.df['MC Percent Change'],
                        visible = False,
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
                            color = time_data['MC_pc_bin'],
                            cmax = time_data['MC_pc_bin'].max(),
                            colorbar=dict(
                                title="Log Microcystin Concentration Change %")
                        )))

        layout = go.Layout(title='Microcystin concentration',
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

        fig = go.Figure(layout=layout, data=traces)    
        return fig
    
    def location_max_avg_yearly(self):
        '''
        Get the maximum location measurements for all locations for a given year
        '''

        year = pd.to_datetime(self.df['DATETIME']).dt.year
        years = range(np.min(year), np.max(year)+1)
        locations = self.get_locations()#list(self.df["Body of Water Name"].unique())
        locations.sort()
        traces = []
        aces = []

        for location in locations:
            loc_data = self.df[self.df["Body of Water Name"] == location]
            loc_year = pd.to_datetime(loc_data['DATETIME']).dt.year
            loc_max = []
            loc_avg = []
            for y in years:
                loc_y_data = loc_data[loc_year == y]
                loc_max.append(np.max(loc_y_data["Microcystin (ug/L)"]))
                loc_avg.append(np.mean(loc_y_data["Microcystin (ug/L)"]))
            
            traces.append(go.Scatter(
                x=np.asarray(years),
                y=np.asarray(loc_max),
                name="Maximum [MC]",
                visible = False
            ))

            traces.append(go.Scatter(
                x=np.asarray(years),
                y=np.asarray(loc_avg),
                name="Average [MC]",
                visible = False
            ))

        layout = go.Layout(
            showlegend=True,
            xaxis=dict(
                title='Year'),
            yaxis=dict(
                title="MC Concentration")) 
        return go.Figure(data=traces, layout=layout)
    
    def tn_tp_mc(self, min_tn=0, max_tn=0, min_tp=0, max_tp=0):

        USEPA_LIMIT = 4
        WHO_LIMIT = 20

        if max_tn == 0:
            max_tn = np.max(self.df["Total Nitrogen (ug/L)"])

        if max_tp == 0:
            max_tp = np.max(self.df["Total Phosphorus (ug/L)"])

        dat = self.df[(self.df["Total Nitrogen (ug/L)"] >= min_tn) & (self.df["Total Nitrogen (ug/L)"] <= max_tn) & (self.df["Total Phosphorus (ug/L)"] >= min_tp) & (self.df["Total Phosphorus (ug/L)"] <= max_tp)]
        MC_conc = dat['Microcystin (ug/L)']
        # make bins
        b1 = dat[MC_conc <= USEPA_LIMIT]
        b2 = dat[(MC_conc > USEPA_LIMIT) & (MC_conc <= WHO_LIMIT)]
        b3 = dat[MC_conc > WHO_LIMIT]

        data = [go.Scatter(
            x=b1["Total Nitrogen (ug/L)"],
            y=b1["Total Phosphorus (ug/L)"],
            mode = 'markers',
            name="<USEPA",
            marker=dict(
                size=8,
                color = "green", #set color equal to a variable
            )),
            go.Scatter(
            x=b2["Total Nitrogen (ug/L)"],
            y=b2["Total Phosphorus (ug/L)"],
            mode = 'markers',
            name=">USEPA",
            marker=dict(
                size=8,
                color = "orange" #set color equal to a variable
            )),
            go.Scatter(
            x=b3["Total Nitrogen (ug/L)"],
            y=b3["Total Phosphorus (ug/L)"],
            mode = 'markers',
            name=">WHO",
            marker=dict(
                size=8,
                color = "red", #set color equal to a variable
            ))]

        layout = go.Layout(
            showlegend=True,
            xaxis=dict(
                title='TN'),
            yaxis=dict(
                title="TP")
            )

        return (go.Figure(data=data, layout=layout))

    def get_locations(self):
        l = []
        locations = list(self.df["Body of Water Name"].unique())
        locations.sort()
        for loc in locations:
            locs = self.df[self.df["Body of Water Name"] == loc]
            locs_years = pd.to_datetime(locs['DATETIME']).dt.year.unique()
            if len(locs_years) > 2:
                l.append(loc)
        return l
    
    def get_df(self):
        return self.df