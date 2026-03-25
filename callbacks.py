from dash import Input, Output, State, ALL, ctx, no_update
import random
import json
import os
from datetime import datetime

COLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
ROWS = [str(i) for i in range(1, 9)]
ALL_SQUARES = [c + r for c in COLS for r in ROWS]

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
        [Output("game-state", "data"),
         Output("target-coordinate", "children"),
         Output("score-display", "children"),
         Output("time-display", "children"),
         Output("timer", "disabled"),
         Output("start-button", "children"),
         Output("highscore-display", "children"),
         Output("feedback-msg", "children"),
         Output("feedback-msg", "className")],
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
            return state, "Click Start!", f"Score: {state['score']}", f"Time: {state['time']}s", True, "Start Game", f"High Score: {state['high_score']}", "", "feedback-msg"
            
        if triggered_id == "start-button":
            if not state["active"]:
                state["active"] = True
                state["score"] = 0
                state["time"] = 60
                state["target"] = random.choice(ALL_SQUARES)
                
                return state, state["target"], f"Score: {state['score']}", f"Time: {state['time']}s", False, "Restart", f"High Score: {state['high_score']}", "Go!", "feedback-msg success-anim"
            else:
                state["score"] = 0
                state["time"] = 60
                state["target"] = random.choice(ALL_SQUARES)
                return state, state["target"], f"Score: {state['score']}", f"Time: {state['time']}s", False, "Restart", f"High Score: {state['high_score']}", "Restarted!", "feedback-msg success-anim"

        if triggered_id == "timer":
            if state["active"]:
                state["time"] -= 1
                if state["time"] <= 0:
                    state["time"] = 0
                    state["active"] = False
                    if state["score"] > state["high_score"]:
                        state["high_score"] = state["score"]
                    save_score(state["score"])
                    return state, "Game Over!", f"Score: {state['score']}", f"Time: 0s", True, "Start Again", f"High Score: {state['high_score']}", "Time's up!", "feedback-msg error-anim"
                
                return state, state["target"], f"Score: {state['score']}", f"Time: {state['time']}s", False, no_update, no_update, no_update, no_update

        if triggered_id and isinstance(triggered_id, dict) and triggered_id.get('type') == 'chess-square':
            if not state["active"]:
                return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
                
            clicked_square = triggered_id['index']
            if clicked_square == state["target"]:
                state["score"] += 1
                state["target"] = random.choice(ALL_SQUARES)
                return state, state["target"], f"Score: {state['score']}", no_update, no_update, no_update, no_update, "+1!", "feedback-msg success-anim"
            else:
                state["score"] -= 1 
                return state, state["target"], f"Score: {state['score']}", no_update, no_update, no_update, no_update, "Wrong!", "feedback-msg error-anim"

        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
