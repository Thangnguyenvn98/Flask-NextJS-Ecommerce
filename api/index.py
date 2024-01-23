from flask import Flask,jsonify

app=Flask(__name__)

@app.route('/api/health', methods=['GET'])
def get():
    return {'Hello': 'world'}


if __name__ == '__main__':
    app.run(debug=True,port=8080)