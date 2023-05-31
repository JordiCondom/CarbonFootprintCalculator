from flask import Flask, config, render_template, request
import pandas as pd
import json
import plotly
import plotly.graph_objects as go

app = Flask(__name__, template_folder='./')

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    country = request.args.get('data')
    return gm(country)

@app.route('/')
def index():
    return render_template('chartsajax.html', graphJSON=gm())

def gm(country='Spain'):
    international_value = 4
    country_values = {'Spain': 6, 'Italy': 10}
    user_value = 10
    global_objective = 0.5
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=['Country', 'International', 'User Value', 'Global Objective'],
                         x=[international_value, country_values[country], user_value, global_objective],
                         marker=dict(
                            color='rgba(50, 171, 96, 0.6)',
                            line=dict(
                                color='rgba(50, 171, 96, 1.0)',
                                width=1),
                        ),
                         orientation='h'),
                         )
    
    
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON

if __name__ == '__main__':
    app.run(debug=True, port=8080)
