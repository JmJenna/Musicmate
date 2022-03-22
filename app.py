import os
import psycopg2
from flask import Flask,abort, request, redirect, render_template , flash, redirect, session, g
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User , Community , Post , Song , Playlist , UserCommu , Likes
from form import UserAddForm , LoginForm , PostForm , ProfileForm
from api import headers
import requests

SEARCH_URL = "https://api.spotify.com/v1"

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',"postgresql:///spotify" )

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chlwjdals492wjddbs')
connect_db(app)



##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])


    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup' , methods=["GET","POST"])
def register_user():
    """Handle user singup. 
       Create new user and add to DB. Redirect to home page"""

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup (
                username = form.username.data,
                password = form.password.data,
                email = form.email.data,
                image_url = form.image_url.data or '/static/images/default-pic.png',
            )

            db.session.commit()

        except IntegrityError:

            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)    
            
        return redirect ('/')
    
    else:

        return render_template('user/signup.html' , form=form)


@app.route('/login' , methods=["GET", "POST"])
def login_user():
    """Handle user login"""

    form = LoginForm()

    if form.validate_on_submit():

        user = User.authenticate(
            form.username.data ,
            form.password.data)
        
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('user/login.html', form=form)



@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    session.pop(CURR_USER_KEY)
    flash('You have successfully logged out', 'danger')
    return redirect('/login')

##############################################################################
# Community

@app.route('/community')
def join_community():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")

    else:    
       
        community = Community.query.all()

        return render_template('community/index.html', community = community)

@app.route('/community/<int:com_id>', methods=['GET','POST']) 
def one_community(com_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")

    else:    
    
        community = Community.query.get_or_404(com_id)
        posts = (Post.query.order_by(Post.id.desc()).all())
        user = g.user
        songs = Song.query.all()

        if request.method == "POST":
            commu = UserCommu(
                user_id =  request.form.get('user_id'),
                commu_id = request.form.get('commu_id')
            )

            db.session.add(commu)
            db.session.commit()

    usercommu = UserCommu.query.all()
    all_commu = Community.query.all()

    return render_template('/community/first_page.html',all_commu=all_commu , community=community , posts=posts, user=user, likes=user.likes, usercommu=usercommu, songs=songs)  
    

@app.route('/community/<int:com_id>/user/<int:user_id>/delete', methods=['GET','POST'])      
def unjoin_community(user_id, com_id):
    """Delete a post"""

    user = User.query.get_or_404(user_id)
    commu = Community.query.get_or_404(com_id)
    user_comm = UserCommu.query.filter(UserCommu.user_id == user.id , UserCommu.commu_id == commu.id).first()    

    db.session.delete(user_comm)
    db.session.commit()
    
    return redirect(f"/community/{commu.id}")

##############################################################################
# Show a list of users 
@app.route('/community/<int:com_id>/users')
def show_all_users(com_id):

    commu = Community.query.get_or_404(com_id)
    users = commu.users

    return render_template('/user/list_users.html', commu=commu , users=users)


##############################################################################
# Handle posts (Users can upload , edit and delete posts)

@app.route('/community/<int:commu_id>/posts/add' , methods=["GET", "POST"] )
def add_post(commu_id):
    """add post"""

    form = PostForm() 

    user_id = session[CURR_USER_KEY]
    songs = [(s.id , s.title ) for s in Song.query.filter(Song.user_id == user_id).all() ]
    form.song_id.choices = songs
    
    commu = Community.query.get_or_404(commu_id)  

    if form.validate_on_submit():

        title = form.title.data
        content = form.content.data
        song_id = form.song_id.data
        commu_id = commu.id

        new_post = Post(title=title , content=content ,song_id=song_id, commu_id=commu_id ,user_id=user_id)
        
        db.session.add(new_post)
        db.session.commit()


        return redirect(f"/community/{commu_id}")

    else:

        return render_template('/post/add.html', form=form , commu=commu)    
      


@app.route('/posts/<int:post_id>/edit' , methods=["GET", "POST"])
def edit_post(post_id):

    post =Post.query.get_or_404(post_id)

    form = PostForm(obj=post)
    user_id = session[CURR_USER_KEY]
    songs = [(s.id , s.title) for s in Song.query.filter(Song.user_id == user_id).all() ]
    form.song_id.choices = songs
    
    if form.validate_on_submit():

        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        
        return redirect(f"/community/{post.commu_id}")

    else:
        return render_template('/post/edit.html', form=form , post=post)


@app.route('/posts/<int:post_id>/community/<int:com_id>/delete', methods=["GET","POST"])
def delete_post(post_id, com_id):
    """Delete a post"""

    post = Post.query.get_or_404(post_id)
    commu = Community.query.get_or_404(com_id)

    db.session.delete(post)
    db.session.commit()
    
    return redirect(f'/community/{commu.id}')

##############################################################################
# Search Song

@app.route('/search', methods=['GET','POST'])
def search_song():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")

    else:    
        q = request.args.get('artist')

        params = {
            "q": q,
            "type": "track",
            "limit": "10"
            }

        res = requests.get(f'{SEARCH_URL}/search', params=params, headers=headers)
        data = res.json()
        tracks = data["tracks"]["items"]

        user = session[CURR_USER_KEY]

        if request.method == "POST":

            song = Song(
            images = request.form.get('track_image'),
            title = request.form.get('track_title'),
            artist = request.form.get('track_artist'),
            link = request.form.get('track_link'),
            user_id = session[CURR_USER_KEY]
            )

            db.session.add(song)
            db.session.commit()
            
            playlist = Playlist(
                song_id = song.id,
                user_id = session[CURR_USER_KEY]
            )
            
            db.session.add(playlist)
            db.session.commit()

    
        return render_template('user/search.html', tracks=tracks , user=user , q=q)

##############################################################################
# Show user page (profile , posts , communities)
@app.route('/users/<int:user_id>')
def show_user_profile(user_id):
    """Show user's profile"""
    user = User.query.get_or_404(user_id)
    
    return render_template('/user/show_profile.html', user=user)


@app.route('/users/<int:user_id>/posts')
def show_user_post(user_id):
    """Show user's posts"""

    user = User.query.get_or_404(user_id)    
    
    return render_template('/user/show_post.html', user=user)

@app.route('/users/<int:user_id>/communities')
def show_communities(user_id):
    """Show user's communities"""

    user = User.query.get_or_404(user_id)

    communities = user.communities

    return render_template('/user/show_community.html', user=user , communities=communities)

##############################################################################
# Show playlist // users can delete song on their playlist

@app.route('/users/<int:user_id>/playlist')
def show_playlist(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
     
    return render_template('user/playlist.html', user=user , songs=user.songs )


@app.route('/users/<int:user_id>/playlist/<int:song_id>/delete',  methods=["GET","POST"])
def delete_song(user_id, song_id):
    """Delete a song"""
    
    user = User.query.get_or_404(user_id)
    song = Song.query.get_or_404(song_id)

    db.session.delete(song)
    db.session.commit()
    
    return redirect(f"/users/{user.id}/playlist")


##############################################################################
# LIKE

@app.route('/users/<int:user_id>/likes', methods=["GET"])
def show_likes(user_id):
    """Show user's liked posts"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    songs = Song.query.all()
    
    likes = user.likes

    return render_template('user/likes.html', user=user , songs=songs , likes=likes)

@app.route('/posts/<int:post_id>/likes', methods=['POST'])
def add_like(post_id):
    """Toggle a liked post for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    liked_post = Post.query.get_or_404(post_id)

    if liked_post.user_id == g.user.id:
        return abort(403)

    user_likes = g.user.likes
   
    if liked_post in user_likes:
        g.user.likes = [like for like in user_likes if like != liked_post]
    else:
        g.user.likes.append(liked_post)

    db.session.commit()
    
   

    return redirect(f"/community/{liked_post.communities.id}")
  

##############################################################################
# Handle user profile
@app.route('/users/<int:user_id>/profile', methods=['GET','POST'])
def edit_user_profile(user_id):
    """Edit user's profile"""

    user = User.query.get_or_404(user_id)

    form = ProfileForm()
    
    if form.validate_on_submit():
        
        user.username = form.username.data,
        user.password = form.password.data,
        user.image_url = form.image_url.data or '/static/images/default-pic.png',
        user.email = form.email.data
        
        db.session.commit()

        return redirect(f"/users/{user.id}")

    else:
        return render_template('user/edit_profile.html', form=form)    

@app.route('/users/<int:user_id>/delete',  methods=["GET","POST"])
def delete_user(user_id):
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect("/signup")

##############################################################################
# Homepage 
@app.route('/')
def homepage():
    """render homepage"""

    return render_template('home_none.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

