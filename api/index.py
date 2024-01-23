from flask import Flask,jsonify
from flask_cors import CORS

app=Flask(__name__)
CORS(app)
@app.route('/api/health', methods=['GET'])
def get():
    return {'Hello': 'world'}


if __name__ == '__main__':
    app.run(debug=True,port=8080)