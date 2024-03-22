import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd


from src.app_utility.dates import get_most_recent_august_start
from src.app_utility.create_output_tables import get_team_and_league_data, get_team_and_league_data_filtered_summarised
from src.data_prep.load_data import (
    get_league_data)

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Pre Processing
latest_season_start = get_most_recent_august_start()

store = dcc.Store(id='hidden-data',
                  data={
                  }
                  ) 

intro = html.Div(
    [
        dbc.Row([
            dbc.Col(width=10, children=[html.H3(children=["FPL Tool | League History"])]),
            dbc.Col(width=2, children=[
                html.Div(children=[html.Img(src='assets/pwt.png', style={'max-height': '100%'})]
                         , style={'height': '50px', 'overflow': 'hidden', 'text-align': 'right'}
                         )
            ])
        ]
        )
    ]
)

select_inputs = html.Div(children=[
    dbc.Row(children=[
        dbc.Col(width=6, children=[
            html.H6('Enter League ID'),
            dcc.Input(id='league-id', type='number', min=0, max=999999999, step=1, style={'width': '90%'}),
            html.Div('This can be obtained from the league URL:',style={'font-style': 'italic'}),
            html.Div('https://fantasy.premierleague.com/leagues/XXXXXX/standings/c',style={'font-style': 'italic'}),
        ]),
        dbc.Col(width=6,children=[
            html.H6('Select League Starting Season'),
            dcc.RangeSlider(
                id='year-select',
                count=1,
                min=2002,
                max=latest_season_start,
                step=1,
                value=[2002],
                marks={year: str(year) if year % 5 == 0 else '' for year in range(2002, latest_season_start + 1)},
                tooltip={"placement": "bottom", "always_visible": True}
                )
            ])
    ]),
])

league_summary_table = html.Div(
    [
        dbc.Row([
            dbc.Col(width=10, children=[html.H3(children=["FPL Tool | League History"])]),
            dbc.Col(width=4, children=[
            dcc.Loading(type="circle", children=[
                html.Div(id='manager-data', children=[
                    ''
                ]
                         )
            ])
        ])
        ]
        )
    ]
)



# Enclosing both intro and select_inputs within a grey box
container = dbc.Card(
    [
        dbc.CardBody([intro, select_inputs]),
    ],
    style={'background-color': '#f8f9fa', 'padding': '20px', 'margin': '20px'}
)

app.title = 'FPL - Complimenting Fixtures'
app.layout = dbc.Container([
    store,
    container,
    league_summary_table
])



@app.callback(
    Output(component_id='manager-data', component_property='children'),
    Input(component_id='league-id', component_property='value'),)
def dash_get_team_and_league_data(league_id):
    """
    This takes the league_id as the dashboard input and returns the data for the league
    """

    print(f'###########{league_id}############')
    league_data, manager_information, team_ids, final_gw_finished, season_history, season_current_df, season_history_df = get_team_and_league_data(league_id=league_id)   
    manager_information=pd.DataFrame(manager_information)



    return dash_table.DataTable(
        id='df',
        columns=[
            {"name": i, "id": i} for i in sorted(manager_information.columns)
        ],
        style_cell={'textAlign': 'center'},
        data=manager_information.to_dict(orient='records'),
        export_format="csv"
    )

# @app.callback(
#     Output(component_id='hidden-data', component_property='data'),
#     Input(component_id='league-id', component_property='value'),
#     [State(component_id='hidden-data', component_property='data')])
# def dash_get_team_and_league_data(league_id,hidden_data):
#     """
#     This takes the league_id as the dashboard input and returns the data for the league
#     """
#     league_data, manager_information, team_ids, final_gw_finished, season_history, season_current_df, season_history_df = get_team_and_league_data(league_id=league_id)   
#     manager_information=pd.DataFrame(manager_information).to_dict(orient='records') 

#     return manager_information


# @app.callback(
#     [Output(component_id='league-summary-kpis', component_property='data')],
#     Input(component_id='year-select', component_property='value'),
#     [State(component_id='hidden-data', component_property='data')]
# )
# def generate_table(year_select, hidden_data):
#     print(hidden_data.keys)
#     print(year_select)
#     #team_and_league_data_filtered_summarised = get_team_and_league_data_filtered_summarised(team_and_league_data=hidden_data,season_start_year=year_select)
#     #league_summary_kpis=team_and_league_data_filtered_summarised['league_summary_kpis']
    
#     return dash_table.DataTable(
#         id='df',
#         style_cell={'textAlign': 'center'},
#         data=hidden_data,
#         export_format="csv"
#     )




if __name__ == '__main__':
    app.run_server(debug=False)
