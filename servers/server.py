from flask import Flask, jsonify
import os


app = Flask(__name__)
app.config.from_pyfile('config.py')


@app.route('/files')
def index():
    """Get all files in a given directory"""
    uploaded_files = os.listdir(app.config.get('FILE_UPLOAD_FOLDER'))
    return jsonify({'uploaded_files': uploaded_files})


if __name__ == "__main__":
    app.run()