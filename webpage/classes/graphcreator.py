import base64
import io
from matplotlib.figure import Figure
import numpy as np
import plotly.graph_objects as go


class graphCreator:
    def __init__(self):
        pass

    def create_pie_chart(self, pie_labels,pie_variable_values):

        total_co2 = int(sum(pie_variable_values))
        pie_variable_values_in_tones = [value / 1000 for value in pie_variable_values]

        piefig = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_variable_values_in_tones, hole=0.5)])

        piefig.update_layout(
            annotations=[
                dict(
                    text= str(total_co2/1000) + "\n tons of CO2",  # The message you want to display
                    x=0.5,  # X position of the annotation (0.5 means center horizontally)
                    y=0.5,  # Y position of the annotation (0.5 means center vertically)
                    showarrow=False,
                    font=dict(size=10)
                )
            ],
            height=500, 
            width=700
        )   

        # Convert the figure to a JSON string
        pie_graph_data = piefig.to_json()
        return pie_graph_data
    
    def create_horizontal_bars(self, x, y, country_average):
        horizontal_bar_fig = go.Figure()

        horizontal_bar_fig.add_trace(go.Bar(
            x=x,
            y=y,
            marker=dict(
                color='rgba(50, 171, 96, 0.6)',
                line=dict(
                    color='rgba(50, 171, 96, 1.0)',
                    width=1),
            ),
            name='CO2 emissions 1',
            orientation='h',
        ))

        horizontal_bar_fig.update_layout(
            title='CO2 emissions by country',
            yaxis=dict(
                showgrid=False,
                showline=False,
                showticklabels=True,
            ),
            xaxis=dict(
                zeroline=False,
                showline=False,
                showticklabels=True,
                showgrid=True,
            ),
            legend=dict(
                x=0.029,
                y=1.038,
                font_size=10
            ),
            margin=dict(l=100, r=20, t=70, b=70),
            paper_bgcolor='rgb(248, 248, 255)',
            plot_bgcolor='rgb(248, 248, 255)',
        )

        # Update the country average value in the figure
        '''
        y_list = list(horizontal_bar_fig['data'][0]['y'])
        y_list[1] = country_average
        horizontal_bar_fig['data'][0]['y'] = tuple(y_list)
        '''

        horizontal_bar_data = horizontal_bar_fig.to_json()
        return horizontal_bar_data
