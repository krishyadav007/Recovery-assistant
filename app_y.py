from flask import Flask, render_template, request, jsonify
import os
import openai_funcs
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        print(file_path)
    
    return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    # Simulate a response from the bot
    response = f"Bot response to: {message}"
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)