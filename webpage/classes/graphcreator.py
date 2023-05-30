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

        print("values: ", pie_variable_values)

        piefig = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_variable_values, hole=0.5, title="Tons of CO2")])

        piefig.update_layout(
            annotations=[
                dict(
                    text= str(total_co2) + "\n tons of CO2",  # The message you want to display
                    x=0.5,  # X position of the annotation (0.5 means center horizontally)
                    y=0.5,  # Y position of the annotation (0.5 means center vertically)
                    showarrow=False,
                    font=dict(size=10)
                )
            ]
        )   

        # Convert the figure to a JSON string
        pie_graph_data = piefig.to_json()
        return pie_graph_data
    
    def create_horizontal_bars(self):
        pass
