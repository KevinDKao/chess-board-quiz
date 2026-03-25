from dash import Input, Output, State, ALL, ctx, no_update, html, dash_table
import plotly.express as px
import pandas as pd
import random
import json
import os
from datetime import datetime
import numpy as np

from layouts import generate_board

COLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
ROWS = [str(i) for i in range(1, 9)]
ALL_SQUARES = [c + r for c in COLS for r in ROWS]
ALL_SQUARES_SORTED = sorted(ALL_SQUARES)

def get_square_classes(clicked_idx=None, is_correct=None):
    classes = []
    for sq in ALL_SQUARES_SORTED:
        c = sq[0]
        r = int(sq[1])
        c_idx = COLS.index(c)
        is_light = (8 - r + c_idx) % 2 == 0
        base = "light-square" if is_light else "dark-square"
        if sq == clicked_idx:
            base += " flash-correct" if is_correct else " flash-incorrect"
        classes.append(f"chess-square {base}")
    return classes

def save_score(score):
    record = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "score": score}
    filename = "scores.json"
    scores = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                scores = json.load(f)
            except Exception:
                pass
    scores.append(record)
    with open(filename, "w") as f:
        json.dump(scores, f, indent=4)

def register_callbacks(app):
    @app.callback(
        Output("board-container", "children"),
        Input("flip-board-switch", "value"),
        prevent_initial_call=True
    )
    def update_board_flip(flipped):
        return generate_board(flipped)

    @app.callback(
        [Output("game-state", "data"),
         Output("target-coordinate", "children"),
         Output("score-display", "children"),
         Output("time-display", "children"),
         Output("time-display", "className"),
         Output("timer", "disabled"),
         Output("start-button", "children"),
         Output("highscore-display", "children"),
         Output("feedback-msg", "children"),
         Output("feedback-msg", "className"),
         Output({'type': 'chess-square', 'index': ALL}, 'className')],
        [Input("start-button", "n_clicks"),
         Input("timer", "n_intervals"),
         Input({'type': 'chess-square', 'index': ALL}, 'n_clicks')],
        [State("game-state", "data")],
        prevent_initial_call=True
    )
    def update_game(start_clicks, n_intervals, square_clicks, state):
        if state is None:
            state = {"active": False, "score": 0, "time": 60, "target": "", "high_score": 0}

        triggered_id = ctx.triggered_id
        
        if not triggered_id:
            return state, "Click Start!", f"Score: {state['score']}", f"Time: {state['time']}s", "time-display", True, "Start Game", f"High Score: {state['high_score']}", "", "feedback-msg", get_square_classes()
            
        if triggered_id == "start-button":
            if not state["active"]:
                state["active"] = True
                state["score"] = 0
                state["time"] = 60
                state["target"] = random.choice(ALL_SQUARES)
                
                return state, state["target"], f"Score: {state['score']}", f"Time: {state['time']}s", "time-display", False, "Restart", f"High Score: {state['high_score']}", "Go!", "feedback-msg success-anim", get_square_classes()
            else:
                state["score"] = 0
                state["time"] = 60
                state["target"] = random.choice(ALL_SQUARES)
                return state, state["target"], f"Score: {state['score']}", f"Time: {state['time']}s", "time-display", False, "Restart", f"High Score: {state['high_score']}", "Restarted!", "feedback-msg success-anim", get_square_classes()

        if triggered_id == "timer":
            if state["active"]:
                state["time"] -= 1
                time_class = "time-display time-critical" if state["time"] <= 5 and state["time"] > 0 else "time-display"
                
                if state["time"] <= 0:
                    state["time"] = 0
                    state["active"] = False
                    if state["score"] > state["high_score"]:
                        state["high_score"] = state["score"]
                    save_score(state["score"])
                    return state, "Game Over!", f"Score: {state['score']}", f"Time: 0s", "time-display", True, "Start Again", f"High Score: {state['high_score']}", "Time's up!", "feedback-msg error-anim", get_square_classes()
                
                return state, state["target"], f"Score: {state['score']}", f"Time: {state['time']}s", time_class, False, no_update, no_update, no_update, no_update, [no_update]*64

        if triggered_id and isinstance(triggered_id, dict) and triggered_id.get('type') == 'chess-square':
            if not state["active"]:
                return (no_update,) * 10 + ([no_update]*64,)
                
            clicked_square = triggered_id['index']
            time_class = "time-display time-critical" if state["time"] <= 5 else "time-display"
            
            if clicked_square == state["target"]:
                state["score"] += 1
                state["target"] = random.choice(ALL_SQUARES)
                return state, state["target"], f"Score: {state['score']}", f"Time: {state['time']}s", time_class, no_update, no_update, no_update, "+1!", "feedback-msg success-anim", get_square_classes(clicked_square, True)
            else:
                state["score"] -= 1
                return state, state["target"], f"Score: {state['score']}", f"Time: {state['time']}s", time_class, no_update, no_update, no_update, "Wrong!", "feedback-msg error-anim", get_square_classes(clicked_square, False)

        return (no_update,) * 10 + ([no_update]*64,)

    @app.callback(
        [Output("score-graph", "figure"),
         Output("box-graph", "figure"),
         Output("stats-summary", "children"),
         Output("recent-scores-table", "children")],
        [Input("tabs", "active_tab")]
    )
    def update_stats(active_tab):
        if active_tab == "tab-stats":
            if os.path.exists("scores.json"):
                with open("scores.json", "r") as f:
                    try:
                        data = json.load(f)
                        df = pd.DataFrame(data)
                    except Exception:
                        df = pd.DataFrame()
            else:
                df = pd.DataFrame()

            empty_fig = px.scatter(title="No data available yet.")
            empty_fig.update_layout(template="plotly_dark", plot_bgcolor="#16213e", paper_bgcolor="#16213e", font_color="#fff")

            if df.empty:
                return empty_fig, empty_fig, "Play a game to see your stats here.", html.Div("No recent scores.")

            df['date'] = pd.to_datetime(df['date'])
            df_sorted = df.sort_values("date")
            
            # Line chart
            fig_line = px.line(df_sorted, x="date", y="score", title="Score Trend", markers=True)
            fig_line.update_layout(
                template="plotly_dark",
                plot_bgcolor="#16213e",
                paper_bgcolor="#16213e",
                font_color="#fff",
                xaxis_title="",
                yaxis_title="Score",
                margin=dict(l=40, r=40, t=60, b=40),
            )
            fig_line.update_xaxes(
                ticklabelmode="period",
                tickformat="%b %d<br>%I:%M %p",
                tickangle=0
            )
            fig_line.update_traces(line_color="#e94560", marker_color="#00a8ff", marker_size=8)

            # Box plot
            df_sorted['day'] = df_sorted['date'].dt.strftime('%b %d')
            fig_box = px.box(df_sorted, x="day", y="score", title="Spread by Day", points="all")
            fig_box.update_layout(
                template="plotly_dark",
                plot_bgcolor="#16213e",
                paper_bgcolor="#16213e",
                font_color="#fff",
                xaxis_title="Day",
                yaxis_title="Score Distribution",
                margin=dict(l=40, r=40, t=60, b=40)
            )
            fig_box.update_traces(marker_color="#4cd137", line_color="#4cd137")

            avg_score = df_sorted['score'].mean()
            max_score = df_sorted['score'].max()
            std_score = df_sorted['score'].std()
            if pd.isna(std_score):
                std_score = 0
            games_played = len(df_sorted)
            
            box_style = {
                "background": "rgba(0,168,255,0.1)", 
                "border": "1px solid #00a8ff", 
                "padding": "15px 20px",
                "borderRadius": "10px",
                "textAlign": "center",
                "minWidth": "140px",
                "boxShadow": "0 4px 6px rgba(0,0,0,0.3)"
            }
            summary = [
                html.Div([html.H2(f"{games_played}", style={"margin": "0"}), html.Small("Games Played")], style=box_style),
                html.Div([html.H2(f"{max_score}", style={"margin": "0"}), html.Small("Personal Best")], style=box_style),
                html.Div([html.H2(f"{avg_score:.1f}", style={"margin": "0"}), html.Small("Average Score")], style=box_style),
                html.Div([html.H2(f"±{std_score:.1f}", style={"margin": "0"}), html.Small("Score Variance")], style=box_style),
            ]
            
            # Recent scores table (Top 10)
            recent_df = df_sorted.sort_values("date", ascending=False).head(10).copy()
            recent_df['date'] = recent_df['date'].dt.strftime("%b %d, %Y %I:%M %p")
            
            table = dash_table.DataTable(
                data=recent_df.to_dict('records'),
                columns=[
                    {"name": "Date & Time", "id": "date"},
                    {"name": "Score", "id": "score"}
                ],
                style_header={
                    'backgroundColor': '#0f3460',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'border': '1px solid #16213e'
                },
                style_cell={
                    'backgroundColor': '#1a1a2e',
                    'color': 'white',
                    'textAlign': 'center',
                    'border': '1px solid #16213e',
                    'padding': '10px'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#16213e'
                    }
                ],
                style_table={'overflowX': 'auto', 'borderRadius': '10px', 'marginTop': '10px'},
                page_action='none'
            )
            
            return fig_line, fig_box, summary, table
            
        return no_update, no_update, no_update, no_update
