from flask import jsonify, request, make_response
from app import create_app
from flask.ext.pymongo import PyMongo
from flask.ext.cors import cross_origin
from utilities import ObjectIdCleaner
from lxml.html import parse
from urlnorm import urlnorm
import bson.objectid as oid
import gridfs
import pymongo

app = create_app()
mongo = PyMongo(app)


@app.before_first_request
def set_before_request_handlers():
    mongo.db.add_son_manipulator(ObjectIdCleaner())


@app.route('/files')
@cross_origin()
def index():
    """Get files.
    FIXME: Add pagination."""
    # fsHandler = GridFS(mongo.db)
    # files = fsHandler.list()
    files = [f for f in mongo.db.urls.find()]
    for f in files:
        if mongo.db.tags.find_one({'fileID':
                                   oid.ObjectId(f.get('id'))}) is None:
            f['tags'] = []
        else:
            f['tags'] = mongo.db.tags.find_one({'fileID':
                                                oid.ObjectId(
                                                    f.get('id'))})['tags']
    return jsonify({'files': files})


@app.route('/static/<ObjectId:id>')
@cross_origin()
def get_upload(id):
    """
    Return the file
    """
    fsHandler = gridfs.GridFS(pymongo.MongoClient()[app.config.get(
        'MONGO_DBNAME')])
    response = make_response()
    f = fsHandler.get(id)
    response.data = f.read()
    return response


@app.route('/upload', methods=['POST'])
def upload():
    """Upload a file.
    TODO: Add support for bulk upload."""
    mongo.save_file(request.files['file'].filename, request.files['file'],
                    content_type=request.files['file'].mimetype)
    return make_response()

    # tags:{'settags':[], 'sugestedtags':[{'who':'dinesh',
    # 'tag':['test','drupal'], 'created': 'date'}]}


@app.route('/tags/<ObjectId:id>', methods=['POST'])
@cross_origin()
def set_tags(id):
    """Update tags for a given file, create the tags if it is not present.
    id is the file id"""
    if mongo.db.tags.find_one({'fileID': id}) is not None:
        mongo.db.tags.update({'fileID': id},
                             {"$set":
                              {"tags": request.form.getlist('tags[]')}})
    else:
        mongo.db.tags.save({'fileID': id,
                            'tags': request.form.getlist('tags[]')})
    return make_response()


@app.route('/user', methods=['GET', 'POST'])
@cross_origin()
def check_user():
    if request.method == 'GET':
        print repr(request.args)
        user = mongo.db.app_users.find_one_or_404({'phone':
                                                   request.args.get('phone'),
                                                   'passkey':
                                                   request.args.get('key')})
        return jsonify({'user': user})
    else:
        user = mongo.db.app_users.find_one({'phone':
                                            request.form.get('phone')})
        if user is None:
            mongo.db.app_users.save({'phone':
                                     request.form.get('phone'),
                                     'isAdmin': True})
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'failed',
                            'reason': 'User already exists'})


@app.route('/url', methods=['POST'])
@cross_origin()
def import_url():
    content = parse(urlnorm(request.form.get('url'))).getroot()
    content.make_links_absolute(urlnorm(request.form.get('url')), True)
    count = 0
    for link in content.iterlinks():
        if link[0].tag == 'a' and link[0].getparent().tag == 'td' and link[0].text != 'Parent Directory':
            mongo.db.urls.save({'url': urlnorm(link[2]),
                                'uploadDate': link[0].getparent()
                                .getnext().text.strip()})
            count += 1
    if count > 0:
        return jsonify({'count': count,
                        'status': 'success'})
    else:
        return jsonify({'count': count,
                        'status': 'error'})


if __name__ == "__main__":
    app.run(host=app.config.get('HOST'))
