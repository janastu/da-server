from flask import jsonify, request, make_response
from app import create_app
from flask.ext.pymongo import PyMongo
from utilities import ObjectIdCleaner
import gridfs
import pymongo

app = create_app()
mongo = PyMongo(app)


@app.before_first_request
def setBeforeRequestHandlers():
    mongo.db.add_son_manipulator(ObjectIdCleaner())


@app.route('/files')
def index():
    """Get files.
    FIXME: Add pagination."""
    # fsHandler = GridFS(mongo.db)
    # files = fsHandler.list()
    files = [f for f in mongo.db.fs.files.find()]
    return jsonify({'files': files})


@app.route('/static/<ObjectId:id>')
def get_upload(id):
    """
    Return the file
    """
    # print repr(mongo.send_file(request.args.get('filename'), base='fs',
    #                            version=0))
    fsHandler = gridfs.GridFS(pymongo.MongoClient()[app.config.get(
        'MONGO_DBNAME')])
    response = make_response()
    f = fsHandler.get(id)
    response.data = f.read()
    return response


@app.route('/upload', methods=['POST'])
def upload():
    mongo.save_file(request.files['file'].filename, request.files['file'],
                    content_type=request.files['file'].mimetype)
    return make_response()


if __name__ == "__main__":
    app.run()