from flask import Flask, jsonify
from process_data import process_data

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def get_data():
    return jsonify(process_data().to_dict(orient='rows'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)