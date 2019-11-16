import os
import numpy as np
import pandas as pd
import json

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

## Load data
current_path = os.path.dirname(os.path.realpath(__file__)) + '/'
data = pd.read_csv(current_path + 'data.csv')
data = data.set_index(['CELL', 'TIMESTAMP'])
cell_list = [int(cell) for cell in data.index.unique(level=0)]
# display(data, cell_list)

### Define figure
def update_figure(cell, ranges):
    
    # Filter cell
    filtered_data = data.xs(key=cell, level=0)

    #Add shapes
    shapes_list = []
    if ranges is not None:
        for range_ in ranges:
            for date in range_:
                ## TODO : compute height dynamically based on graph's max and min
                shapes_list.append(
                    {
                        'type': 'line',
                        'x0': date,
                        'y0': 2.8,
                        'x1': date,
                        'y1': 3.5,
                        'line': {
                            'color': 'black',
                            'width': 1.25,
                        },
                    },
                )


    return {
        'data': [
            
            go.Scattergl(
                name = 'Voltage',
                x = filtered_data.index,
                y = filtered_data.V_CELL,
                mode = 'lines+markers',
                marker=dict(
                    size = 2,
                    color = '#F18F01', 
                ),
                line=dict(
                    width = 2,
                )
            ),

            go.Scattergl(
                name = 'Current',
                x = filtered_data.index,
                y = filtered_data.I_MAIN,
                mode = 'lines+markers',
                marker=dict(
                    size = 2,
                    color = '#048BA8', 
                ),
                line=dict(
                    width = 2,
                ),
                yaxis='y2',
            ),
            
            go.Scattergl(
                name = 'Temperature',
                x = filtered_data.index,
                y = filtered_data.T_CATH_OUT,
                mode = 'lines+markers',
                marker=dict(
                    size = 2,
                    color = '#2E4057', 
                ),
                line=dict(
                    width = 2,
                ),
                yaxis='y3',
            ),
            
            go.Scattergl(
                name = 'Caustic',
                x = filtered_data.index,
                y = filtered_data.X_CONC_CAUST_OUT,
                mode = 'lines+markers',
                marker=dict(
                    size = 2,
                    color = '#99C24D', 
                ),
                line=dict(
                    width = 2,
                ),
                yaxis='y4',
            ),
        ],

        'layout': go.Layout(
            clickmode = 'event',
            dragmode = 'select',

            title = 'Interactive Dates Selection',
            title_font=dict(
                size=20
            ),

            font =dict(
                family='Times New Roman',
                size=14,
                color='black'
            ),

            xaxis = dict(
                # Text
                title_text='Time',

                # Grid
                showgrid = True,
                zeroline= False,

                #Border
                showline=True,
                linewidth=1.25,
                linecolor='black',

                # Extra
                # tickformat = '%d %B<br>%a'
            ),

            yaxis = dict(
                # Title
                title_text='Voltage (V)',

                # Grid
                showgrid = True,
                zeroline= False,

                # Border
                showline=True,
                linewidth=1.25,
                linecolor='black',

                # Extra
                exponentformat="none",
                domain=[0, 0.25],
            ),

            yaxis2 = dict(
                # Title
                title_text='Current (kA)',

                # Grid
                showgrid = True,
                zeroline= False,

                # Border
                showline=True,
                linewidth=1.25,
                linecolor='black',

                # Extra
                exponentformat="none",
                domain=[0.3, 0.5],
            ),

            yaxis3 = dict(
                # Title
                title_text='Temperature (C)',

                # Grid
                showgrid = True,
                zeroline= False,

                # Border
                showline=True,
                linewidth=1.25,
                linecolor='black',

                # Extra
                exponentformat="none",
                domain=[0.55, 0.75],
            ),

            yaxis4 = dict(
                # Title
                title_text='Caustic Concentration(%)',

                # Grid
                showgrid = True,
                zeroline= False,

                # Border
                showline=True,
                linewidth=1.25,
                linecolor='black',

                # Extra
                exponentformat="none",
                domain=[0.8, 1],
            ),

            showlegend=True,
            legend = dict(
                traceorder="reversed",
            ),

            shapes=shapes_list,
        )
    }

## Calculate u0 and k
def calculate_parameters(cell, range_list):

    ## TODO: filter pd.Dataframe by cell and pair of dates
    pass


### HTML layout
app = dash.Dash()
app.layout = html.Div([

    dcc.Graph(
        id='figure',
        style={
            'height': '75vh'
        }
    ),

    dcc.Dropdown(
        id='chosen_cell',
        options=[{'label': 'Cell ' + str(cell), 'value': cell} for cell in cell_list],
        value=cell_list[0],
    ),

    html.Div([
        dcc.Markdown(
            """
            **Selected Dates**. 
            _Double-click anywhere on the graph while on selection mode to reset.
            When a different cell is selected, the selection is also resetted._
            """
        ),

        html.Pre(id='text-output',
                style={
                    'border': 'thin lightgrey solid',
                    'overflowX': 'scroll',
                }
        )
    ]),
])
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


### Callbacks
range_list = []
previous_cell = cell_list[0]

@app.callback(
    [Output('figure', 'figure'), Output('text-output', 'children')],
    [Input('figure', 'selectedData'), Input('chosen_cell', 'value')]
)
def display_selected_data(selectedData, cell):

    # TODO : Make the script not use global variables
    global range_list
    global previous_cell

    # Reset if deselected
    if selectedData is None:
        range_list = []
        figure = update_figure(cell, None)
    
    # If cell changes, reset range
    elif cell != previous_cell:    
        range_list = []
        previous_cell = cell
        figure = update_figure(cell, None)

    else:
        range_list.append(selectedData['range']['x'])
        figure = update_figure(cell, range_list)

    # TODO : Instead of returning the dates, return the calculated parameters
    # parameters = calculate_parameters(cell, range_list)
    # return figure, parameters

    return figure, json.dumps(range_list, indent=2)

    
### Execute
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=80)