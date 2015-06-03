from flask import Flask, jsonify
import os


app = Flask(__name__)
app.config.from_pyfile('config.py')


@app.route('/files')
def index():
    """Get all files in a given directory"""
    uploaded_files = os.listdir(app.config.get('FILE_UPLOAD_FOLDER'))
    upload_info = []
    for upload in uploaded_files:
        upload_item = []
        upload_item.append(upload)
        upload_item.append(float(os.path.getsize(os.path.join(
            app.config.get('FILE_UPLOAD_FOLDER'), upload)))/1024)
        upload_info.append(upload_item)
    return jsonify({'uploaded_files': upload_info})


if __name__ == "__main__":
    app.run()