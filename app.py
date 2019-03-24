import json
from flask import Flask, request
from db import DB

app = Flask(__name__)

db = DB()

posts = {}
comments = {}

@app.route('/')
def root():
    return 'Hello world!'

@app.route('/api/posts/', methods=['GET'])
def get_posts():
    """
    Returns all posts, including their id, score, text, and username fields.
    """
    res = {'success':True, 'data': db.get_posts()}
    return json.dumps(res), 200

@app.route('/api/posts/', methods=['POST'])
def create_post():
    """
    Takes a json with at least a 'text' field, and adds a post with score 0, the
    corresponding text, and the username if there's a 'username' field (otherwise
    "anonymous").
    """
    post_body = json.loads(request.data)
    username = post_body['username'] if 'username' in post_body else "anonymous"
    if not 'text' in post_body:
        return json.dumps({'success':False, 'error':'Empty text field'}), 404
    post = {
        'id': db.create_post(post_body['text'], username),
        'score': 0,
        'text' : post_body['text'],
        'username': username
    }
    res = {'success':True, 'data':post}
    return json.dumps(res), 201

@app.route('/api/post/<int:post_id>/', methods=['GET'])
def get_post(post_id):
    """
    Returns the post corresponding to the given ID, if it exists and hasn't 
    been deleted. 
    """
    post = db.get_post_by_id(post_id)
    if post is not None:
        return json.dumps({'success':True, 'data':post}), 200
    else:
        return json.dumps({'success':False, 'error':'This post doesn\'t exist.'}), 404

@app.route('/api/post/<int:post_id>/', methods=['POST'])
def edit_post(post_id):
    """
    Takes a json with a 'text' field and replaces the text in the post given 
    by the given post id by this text. Returns a 404 error if there's no post
    with that post id.
    """
    post_body = json.loads(request.data)
    if not 'text' in post_body:
        return json.dumps({'success':False, 'error':'Empty text field'}), 404
    db.edit_post_by_id(post_id, post_body['text'])
    updated_post = db.get_post_by_id(post_id)
    if updated_post is not None:
        return json.dumps({'success':True, 'data':updated_post}), 200
    else:
        return json.dumps({'success':False, 'error':'This post doesn\'t exist.'}), 404

@app.route('/api/post/<int:post_id>/', methods=["DELETE"])
def delete_post(post_id):
    """
    Deletes the post associated with the given post id, if it exists. Note that 
    the comments associated with the post still stay. 
    """
    post = db.get_post_by_id(post_id)
    if post is not None:
        db.delete_post_by_id(post_id)
        return json.dumps({'success':True, 'data':post}), 200
    else:
        return json.dumps({'success':False, 'error':'This post doesn\'t exist.'}), 404

@app.route('/api/post/<int:post_id>/comments/', methods=['GET'])
def get_comments(post_id):
    """
    Returns a list of all the comments associated with a given post id, if it
    has not been deleted.
    """
    if db.get_post_by_id(post_id) is not None:
        res = {'success':True, 'data': db.get_comments(post_id)}
        return json.dumps(res), 200
    else:
        return json.dumps({'success':False, 'error':'This post doesn\'t exist.'}), 404


@app.route('/api/post/<int:post_id>/comment/', methods=['POST'])
def post_comment(post_id):
    """
    Appends the given comment to the list of comments associated with the post
    with the given post id, if it exists/has not been deleted. The comment json 
    must have at least a 'text' field.
    """
    comment_body = json.loads(request.data)
    if not 'text' in comment_body:
        return json.dumps({'success':False, 'error':'Empty text field'}), 404
    if db.get_post_by_id(post_id) is None: 
        return json.dumps({'success':False, 'error':'This post doesn\'t exist.'}), 404
    username = comment_body['username'] if 'username' in comment_body else "anonymous"
    comment = {
        'id': db.create_comment(post_id, comment_body['text'], username),
        'score': 0,
        'text' : comment_body['text'],
        'username': username
    }
    res = {'success':True, 'data':comment}
    return json.dumps(res), 201

@app.route('/api/posts/author/<string:username>/', methods=['GET'])
def get_posts_by_username(username):
    """
    Returns all posts authored by the given username, including their id, score,
    text, and username fields.
    """
    res = {'success':True, 'data': db.get_posts_by_username(username)}
    return json.dumps(res), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
