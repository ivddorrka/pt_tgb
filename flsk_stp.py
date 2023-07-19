from flask import Flask, jsonify, redirect, url_for, render_template, request
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView 
import os
from werkzeug.utils import secure_filename
from flask_admin.helpers import url_for
from flask_admin.model.template import macro

UPLOAD_FOLDER = './media'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4'}
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = ""
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






# Custom route for handling admin panel form submission
@app.route('/admin/create_post/', methods=['POST'])
def admin_create_post():
    description = request.form.get('description')
    tags = request.form.get('tags')
    photos = request.files.getlist('photos')
    video = request.files.get('video')

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Save the photos
    photo_paths = []
    for photo in photos:
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_paths.append(filename)

    # Save the video
    video_path = None
    if video and allowed_file(video.filename):
        filename = secure_filename(video.filename)
        video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        video_path = filename

    # Create a new Post object and save it to the database
    new_post = Post(description=description, tags=tags, photos=','.join(photo_paths), video=video_path)
    db.session.add(new_post)
    db.session.commit()

    return redirect(url_for('admin.index'))

class CreatePostView(BaseView):
    @expose('/', methods=['GET'])
    def index(self):
        return self.render('admin/create_post.html', url_for=url_for)










class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(255), nullable=False)
    tags = db.Column(db.String(255))
    photos = db.Column(db.String(255))  # Storing file paths to photos in the database
    video = db.Column(db.String(255))  # Storing file paths to video in the database

    def __repr__(self):
        return f"Post(id={self.id}, description={self.description}, tags={self.tags})"




@app.route('/admin/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': f'Post with ID {post_id} deleted successfully'})
    else:
        return jsonify({'message': f'Post with ID {post_id} not found'}), 404


@app.route('/search_posts_by_tags', methods=['GET', 'POST'])
def search_posts_by_tags():
    search_query = request.args.get('query')


    words = search_query.split()
    posts = []
    posts_id = []
    
    
    
    if len(words)>0:
        posts_prom = Post.query.filter(Post.tags.contains(words[0]))
        if len(words)>1:
            for post in posts_prom:
                for word in words[1:]:
                    if str(word) in post.tags:
                        post_data = [{"id": post.id, "description": post.description, "tags": post.tags, "photos": post.photos, "video": post.video}]
                        posts.append(post_data)
        else:
            post = posts_prom[0]
            post_data = [{"id": post.id, "description": post.description, "tags": post.tags, "photos": post.photos, "video": post.video}]
            posts.append(post_data)
        
    return jsonify(posts), 200

@app.route('/search_posts_by_descs', methods=['GET', 'POST'])
def search_posts_by_desc():
    search_query = request.args.get('query')

    words = search_query.split()
    posts = []
    posts_id = []
    
    posts_prom = Post.query.filter(Post.description.contains(' '.join(words)))
    for post in posts_prom:
            
            post_data = [{"id": post.id, "description": post.description, "tags": post.tags, "photos": post.photos, "video": post.video}]

    
            posts.append(post_data)
   
        
    return jsonify(posts), 200

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return self.username

with app.app_context():
    db.create_all()
    
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))


admin.add_view(CreatePostView(name='Create Post', endpoint='create_post'))

admin.add_view(ModelView(Post, db.session))

if __name__ == "__main__":
    app.debug=True
    app.run()

