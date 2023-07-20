from flask import Flask, jsonify, redirect, url_for, render_template, request, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView 
import os
from werkzeug.utils import secure_filename
from flask_admin.helpers import url_for
from flask_admin.model.template import macro
from config_loader import *


UPLOAD_FOLDER = './media'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4'} # media accptable format

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI # config setup
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

db = SQLAlchemy(app)



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



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    tg_id = db.Column(db.Integer, unique=True, nullable=False)
    
    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, password={self.password})"

# class UserView(ModelView):
#     column_searchable_list = ['username']
#     form_columns = ['username', 'password']

class LoginView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        # Handle the login logic here
        if user_is_authenticated():  
            return redirect(url_for('admin.index'))
        else:
            return render_template('login.html')

class LogoutView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        # Handle the login logic here
        if user_is_authenticated():  
            return redirect('/logout')
        else:
            return render_template('login.html')
# LogoutView

# def user_is_admin(user_id):
    
    
def user_is_authenticated():
    # Assuming you store the user ID in the 'user_id' key of the session
    user_id = session.get('user_id')
    return user_id is not None

def allowed_file(filename):
    ## checking if file is allowed to be submitted
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def start_up():
    if user_is_authenticated():
        return redirect('/admin')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Clear the user_id from the session to log out the user
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Retrieve the user from the database based on the given username
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            # If the login is successful, store the user_id in the session
            session['user_id'] = user.id
            return redirect('/admin')  # Redirect to the dashboard or any other page
        else:
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/admin/create_post/', methods=['POST'])
def admin_create_post():
    tg_id = request.args.get('tg_id') 
    
    if user_is_authenticated() or User.query.filter_by(tg_id=tg_id).first():  
        # post creation on admin panel "Create Post"
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
    else:
        return redirect(url_for('login'))



@app.route('/admin/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # for post deletion access from chat
    tg_id = request.args.get('tg_id') 
    if user_is_authenticated() or User.query.filter_by(tg_id=tg_id).first():  
        post = db.session.get(Post, post_id)
        if post:
            db.session.delete(post)
            db.session.commit()
            return jsonify({'message': f'Post with ID {post_id} deleted successfully'})
        else:
            return jsonify({'message': f'Post with ID {post_id} not found'}), 404
    else:
        return redirect(url_for('login'))


@app.route('/search_posts_by_tags', methods=['GET', 'POST'])
def search_posts_by_tags():
    # search by tags, submitted by user, return posts that have all those tags
    
    search_query = request.args.get('query')

    words = search_query.split()
    posts = []    
    
    if len(words)>0:
        
        posts_prom = Post.query.filter(Post.tags.contains(words[0]))
        post_count = posts_prom.count()

        if post_count > 0:
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

@app.route('/search_all', methods=['GET', 'POST'])
def search_all_posts():
    # search by tags, submitted by user, return posts that have all those tags
    
    posts = Post.query.all()
    posts_data = []
    for post in posts:
        post_data = [{"id": post.id, "description": post.description, "tags": post.tags, "photos": post.photos, "video": post.video}]
        posts_data.append(post_data)
       
        
    return jsonify(posts_data), 200

@app.route('/search_posts_by_descs', methods=['GET', 'POST'])
def search_posts_by_desc():
    # search by piece of description, submitted by user, return posts that have that has user-input as a part of theirs description 
    search_query = request.args.get('query')

    words = search_query.split()
    posts = []
    posts_id = []
    
    posts_prom = Post.query.filter(Post.description.contains(' '.join(words)))
    for post in posts_prom:
            
            post_data = [{"id": post.id, "description": post.description, "tags": post.tags, "photos": post.photos, "video": post.video}]

    
            posts.append(post_data)
   
        
    return jsonify(posts), 200


if __name__ == "__main__":
    
    # with app.app_context():
    #     db.create_all()
        
    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

    admin.add_view(CreatePostView(name='Create Post', endpoint='create_post'))

    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(User, db.session))
    # admin.add_view(UserView(User, db.session))
    admin.add_view(LoginView(name='Login', endpoint='login'))
    admin.add_view(LogoutView(name='Logout', endpoint='logout'))
    
    with app.app_context():
        db.create_all()
        
    app.debug=True
    app.run()


