from flask import Flask, jsonify, request, render_template
import chess
import chess.engine

app = Flask(__name__)

board = chess.Board()
engine_path = r'\.roengine\.ros-engine-windows-x86-64-modern.exe' 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset_game():
    global board
    board = chess.Board()
    return jsonify({"status": "success", "fen": board.fen()})

@app.route('/make_move', methods=['POST'])
def make_move():
    global board
    data = request.json
    user_move = data.get('move')
    try:
        move = chess.Move.from_uci(user_move)
        if move in board.legal_moves:
            board.push(move)
            return jsonify({"status": "success", "fen": board.fen()})
        else:
            return jsonify({"status": "error", "message": "Invalid move!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_suggestion', methods=['GET'])
def get_suggestion():
    global board
    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        result = engine.play(board, chess.engine.Limit(time=2.0))
        suggested_move = result.move.uci()
        return jsonify({"status": "success", "suggestion": suggested_move})

@app.route('/auto_move', methods=['POST'])
def auto_move():
    global board
    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        result = engine.play(board, chess.engine.Limit(time=2.0))
        suggested_move = result.move
        board.push(suggested_move)
        print(f"AI Move: {suggested_move.uci()}") 
        return jsonify({"status": "success", "fen": board.fen(), "move": suggested_move.uci()})

if __name__ == '__main__':
    app.run(debug=True)