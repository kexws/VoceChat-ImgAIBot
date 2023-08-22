from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['GET'])
def webhook():
    return "Hello, this is a GET request!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5321)
