from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import ai
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Dictionary to store file paths associated with each uid
file_paths = {}

@app.route('/')
def index():
    # Generate a new UID
    uid = str(uuid.uuid4())
    # Redirect to the unique session URL
    return redirect(url_for('session', uid=uid))

@app.route('/session/<uid>')
def session(uid):
    return render_template('index.html', uid=uid)

@app.route('/upload/<uid>', methods=['POST'])
def upload_file(uid):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        print(file_path)
        # Store the file path in the dictionary
        file_paths[uid] = file_path
       
    return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

@app.route('/chat/<uid>', methods=['POST'])
def chat(uid):
    # Retrieve the file path based on the uid
    file_path = file_paths.get(uid)
    if not file_path:
        return jsonify({'error': 'File not found for the given UID'}), 400

    # Create the QA agent
    question = request.json.get('message')
    qa_agent = ai.create_qa_agent(file_path)
    result = ai.ask_question(qa_agent, question)
    if result.get("error"):
        print(result['error'])
    else:
        print(f"Answer: {result['answer']}")
        print("Sources used:")
        for i, source in enumerate(result['sources'], 1):
            print(f"Source {i}: {source[:200] + '...' if len(source) > 200 else source}")
 
    # response = f"Bot response to: {question}"
    return jsonify({'response': result['answer']})

if __name__ == '__main__':
    app.run(debug=False)