# Import required libraries
import dash
import pandas as pd
from dash import html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate

# Assume 'app' is your Dash web application
app = dash.Dash(__name__)

# Assume 'data' is your incident data
data = pd.read_csv('datacsv.csv')

# Layout of the web application
app.layout = html.Div([
    html.Div(className="header-container", children=[
        html.Div(className="logo", children=[
            html.Img(src="https://www.nus.edu.sg/images/default-source/identity-images/NUS_logo_full-horizontal.jpg", alt="NUS Logo", style={"height": "100px"})
        ]),
        html.Div(className="header", children=[
            html.H1("NUSecure")
        ]),
        html.Div(className="security-team", children=[
            html.H1("Security Team")
        ]),
    ]),
    
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # in milliseconds, update every 10 seconds
        n_intervals=0
    ),

    dcc.Graph(id='map', config={'scrollZoom': False}),

    html.Button('Open Tab', id='open-tab-button'),

    html.Div(className="overlay", id="overlay", children=[
        html.Div(className="overlay-content", children=[
            html.H2("Filter By:"),
            # ... (Rest of your filter inputs)
            
            html.H2("Incidents Table"),
            html.Button("New Report", id="add-report-button"),
            
            html.Div(id='modal', className='modal', children=[
                html.Div(id='modal-content', className='modal-content', children=[
                    html.H2("Add New Report"),
                    # ... (Form for adding a new report)
                    html.Button("Add", id="add-button"),
                ]),
            ]),
            
            html.Table(id='data-table', children=[
                html.Thead(children=[
                    html.Tr([
                        html.Th("Incident ID"),
                        html.Th("Date"),
                        html.Th("Time"),
                        # ... (Rest of your table headers)
                    ])
                ]),
                html.Tbody(id='data-table-body', children=[
                    # ... (Dynamic rows will be added here)
                ]),
            ]),
        ]),
    ]),
])

# Define callback to open/close the overlay
@app.callback(
    Output('overlay', 'style'),
    Output('modal', 'style'),
    Output('data-table-body', 'children'),
    Input('open-tab-button', 'n_clicks'),
    prevent_initial_call=True
)

def open_tab(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    
    style = {'display': 'block'}
    modal_style = {'display': 'none'}
    table_rows = []

    # ... (Populate table_rows with your data)

    return style, modal_style, table_rows

# Define callback to add a new report
@app.callback(
    Output('data-table-body', 'children'),
    Input('add-button', 'n_clicks'),
    prevent_initial_call=True
)
def add_report(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    
    # ... (Logic to add a new report to the table)

    table_rows = []

    # ... (Populate table_rows with your updated data)

    return table_rows

# ... (Add more callbacks as needed)

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=9001)
