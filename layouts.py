from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

PIECES = {
    'A8': ('♜', 'black-piece'), 'B8': ('♞', 'black-piece'), 'C8': ('♝', 'black-piece'), 'D8': ('♛', 'black-piece'), 'E8': ('♚', 'black-piece'), 'F8': ('♝', 'black-piece'), 'G8': ('♞', 'black-piece'), 'H8': ('♜', 'black-piece'),
    'A7': ('♟', 'black-piece'), 'B7': ('♟', 'black-piece'), 'C7': ('♟', 'black-piece'), 'D7': ('♟', 'black-piece'), 'E7': ('♟', 'black-piece'), 'F7': ('♟', 'black-piece'), 'G7': ('♟', 'black-piece'), 'H7': ('♟', 'black-piece'),
    'A2': ('♟', 'white-piece'), 'B2': ('♟', 'white-piece'), 'C2': ('♟', 'white-piece'), 'D2': ('♟', 'white-piece'), 'E2': ('♟', 'white-piece'), 'F2': ('♟', 'white-piece'), 'G2': ('♟', 'white-piece'), 'H2': ('♟', 'white-piece'),
    'A1': ('♜', 'white-piece'), 'B1': ('♞', 'white-piece'), 'C1': ('♝', 'white-piece'), 'D1': ('♛', 'white-piece'), 'E1': ('♚', 'white-piece'), 'F1': ('♝', 'white-piece'), 'G1': ('♞', 'white-piece'), 'H1': ('♜', 'white-piece'),
}

def generate_board(flipped=False):
    rows = []
    cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    row_range = range(1, 9) if flipped else range(8, 0, -1)
    col_range = cols[::-1] if flipped else cols

    for r in row_range:
        squares = []
        for c in col_range:
            c_idx = cols.index(c)
            square_id = f"{c}{r}"
            is_light = (8 - r + c_idx) % 2 == 0
            color_class = "light-square" if is_light else "dark-square"
            piece_data = PIECES.get(square_id, ("", ""))
            piece = piece_data[0]
            piece_class = piece_data[1]
            
            squares.append(
                html.Div(
                    id={'type': 'chess-square', 'index': square_id},
                    className=f"chess-square {color_class}",
                    children=html.Span(piece, className=f"chess-piece {piece_class}"),
                    n_clicks=0,
                )
            )
        rows.append(html.Div(squares, className="chess-row"))
    return html.Div(rows, className="chess-board")

game_layout = html.Div([
    html.Div([
        html.H1("Chess Coordinate Quiz", className="title"),
        html.Div([
            html.Div("Score: 0", id="score-display", className="score-display"),
            html.Div("Time: 60s", id="time-display", className="time-display"),
            html.Div("High Score: 0", id="highscore-display", className="highscore-display"),
        ], className="stats-container"),
        
        html.Div(id="target-coordinate", className="target-coordinate", children="Click Start!"),
        
        html.Button("Start Game", id="start-button", className="start-btn", n_clicks=0),
        
        html.Div([
            dbc.Switch(id="flip-board-switch", label="Play as Black", value=False, class_name="flip-switch")
        ], style={"marginBottom": "15px", "display": "flex", "justifyContent": "center"}),
        
        html.Div(id="board-container", children=generate_board(flipped=False)),
        
        html.Div(id="feedback-msg", className="feedback-msg"),
        
        dcc.Interval(id="timer", interval=1000, n_intervals=0, disabled=True),
        dcc.Store(id="game-state", data={"active": False, "score": 0, "time": 60, "target": "", "high_score": 0}),
    ], className="game-container")
], className="main-wrapper")

stats_layout = html.Div([
    html.Div([
        html.H1("Performance Stats", className="title"),
        html.Div(id="stats-summary", style={
            "display": "flex", "flexWrap": "wrap", 
            "justifyContent": "center", "gap": "15px", 
            "marginBottom": "20px", "color": "#00a8ff"
        }),
        html.Div(dcc.Graph(id="score-graph", config={'displayModeBar': False}, responsive=True), style={'width': '100%', 'borderRadius': '10px', 'overflow': 'hidden', 'marginBottom': '20px'}),
        html.Div(dcc.Graph(id="box-graph", config={'displayModeBar': False}, responsive=True), style={'width': '100%', 'borderRadius': '10px', 'overflow': 'hidden'}),
        html.H3("Recent Scores", style={"marginTop": "30px", "color": "#e94560", "textAlign": "center"}),
        html.Div(id="recent-scores-table", style={"marginTop": "10px", "width": "100%", "maxWidth": "100%", "overflowX": "auto"})
    ], className="game-container", style={"maxWidth": "800px"})
], className="main-wrapper")

layout = html.Div([
    dbc.Tabs([
        dbc.Tab(game_layout, label="Play Game", tab_id="tab-game", label_style={"color": "#fff", "fontSize": "1.2rem", "fontWeight": "bold"}),
        dbc.Tab(stats_layout, label="Statistics", tab_id="tab-stats", label_style={"color": "#fff", "fontSize": "1.2rem", "fontWeight": "bold"}),
    ], id="tabs", active_tab="tab-game", className="mb-4", style={"justifyContent": "center", "marginTop": "20px"}),
])
