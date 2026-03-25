from dash import html, dcc

def generate_board():
    rows = []
    cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    for r in range(8, 0, -1):
        squares = []
        for c_idx, c in enumerate(cols):
            square_id = f"{c}{r}"
            is_light = (8 - r + c_idx) % 2 == 0
            color_class = "light-square" if is_light else "dark-square"
            
            squares.append(
                html.Div(
                    id={'type': 'chess-square', 'index': square_id},
                    className=f"chess-square {color_class}",
                    n_clicks=0,
                    # children=square_id # uncomment for debugging
                )
            )
        rows.append(html.Div(squares, className="chess-row"))
    return html.Div(rows, className="chess-board")

layout = html.Div([
    html.Div([
        html.H1("Chess Coordinate Quiz", className="title"),
        html.Div([
            html.Div("Score: 0", id="score-display", className="score-display"),
            html.Div("Time: 60s", id="time-display", className="time-display"),
            html.Div("High Score: 0", id="highscore-display", className="highscore-display"),
        ], className="stats-container"),
        
        html.Div(id="target-coordinate", className="target-coordinate", children="Click Start!"),
        
        html.Button("Start Game", id="start-button", className="start-btn", n_clicks=0),
        
        generate_board(),
        
        html.Div(id="feedback-msg", className="feedback-msg"),
        
        dcc.Interval(id="timer", interval=1000, n_intervals=0, disabled=True),
        dcc.Store(id="game-state", data={"active": False, "score": 0, "time": 60, "target": "", "high_score": 0}),
    ], className="game-container")
], className="main-wrapper")
