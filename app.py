from flask import Flask, jsonify, request, render_template
import chess
import chess.engine
import platform

app = Flask(__name__)
board = chess.Board()

current_os = platform.system()
if current_os == "Windows":
    engine_path = r"windows_engine\.ros-engine-windows-x86-64-modern.exe"
elif current_os == "Linux":
    engine_path = r"linux_engine\stockfish-ubuntu-x86-64"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset_game():
    global board
    board = chess.Board()
    return jsonify({"status": "success", "fen": board.fen()})

@app.route('/get_legal_moves', methods=['POST'])
def get_legal_moves():
    global board
    data = request.json
    square = data.get("square")
    try:
        square_index = chess.parse_square(square)
        legal_moves = [
            move.uci() for move in board.legal_moves if move.from_square == square_index
        ]
        return jsonify({"status": "success", "legal_moves": legal_moves})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/make_move', methods=['POST'])
def make_move():
    global board
    data = request.json
    move = data.get("move") 
    try:
        chess_move = chess.Move.from_uci(move)
        if chess_move in board.legal_moves:
            board.push(chess_move)
            return jsonify({"status": "success", "fen": board.fen()})
        else:
            return jsonify({"status": "error", "message": "Invalid move!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_ai_suggestion', methods=['GET'])
def get_ai_suggestion():
    global board
    try:
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            result = engine.play(board, chess.engine.Limit(time=2.0))
            suggested_move = result.move.uci()
            return jsonify({"status": "success", "suggestion": suggested_move})
    except Exception as e:
        print(f"Error with Stockfish: {e}")  # Debugging line
        return jsonify({"status": "error", "message": f"Error using Stockfish: {str(e)}"})


@app.route('/auto_move', methods=['POST'])
def auto_move():
    global board
    try:
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            result = engine.play(board, chess.engine.Limit(time=2.0))
            suggested_move = result.move
            board.push(suggested_move)
            return jsonify({"status": "success", "fen": board.fen(), "move": suggested_move.uci()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
