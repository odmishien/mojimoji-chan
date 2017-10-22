from datetime import datetime
from flask import jsonify
from MadproBot import app

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return jsonify({
        "message": "this endpoint is active"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    reply_to_line(request.json)
    return '', 200, {}

if __name__ == '__main__':
    app.run()