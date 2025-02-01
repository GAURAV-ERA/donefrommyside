from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/forms')
def forms():
    return render_template('forms.html')

@app.route('/model_score')
def model_score():
    return render_template('model_score.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
