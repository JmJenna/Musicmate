from datetime import datetime

from flask_bcrypt import Bcrypt

from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()

db = SQLAlchemy()

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
        default=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    

    password = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default='/static/images/default-pic.png',
    )


    posts = db.relationship("Post", backref='users')

    songs = db.relationship("Song" , secondary="playlist" , backref="users")

    communities = db.relationship("Community",secondary="user_communities" , backref="users")
    
    likes = db.relationship("Post", secondary="likes")
    

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Likes(db.Model):
    """Mapping user likes to posts."""

    __tablename__ = 'likes' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey('posts.id', ondelete='cascade')
    )


class Community(db.Model):

    __tablename__ = 'communities'

    id = db.Column(
            db.Integer, 
            primary_key=True
        )

    genre = db.Column(
        db.Text,
        nullable=False
    )  

class UserCommu(db.Model):

    __tablename__ = "user_communities"    

    user_id = db.Column(db.Integer , db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)

    commu_id = db.Column(db.Integer , db.ForeignKey('communities.id', ondelete='cascade'), primary_key=True)

class Post(db.Model):
    
    __tablename__ = 'posts'

    id = db.Column(
            db.Integer, 
            primary_key=True
        )

    title = db.Column(
        db.Text,
        nullable=False
      )

    content = db.Column(
            db.Text,
            nullable = False
            )

    timestamp = db.Column(
                db.DateTime,
                nullable=False,
                default=datetime.utcnow(),
                )

    song_id = db.Column(db.Integer, db.ForeignKey('songs.id' , ondelete='cascade'))

    commu_id = db.Column(db.Integer, db.ForeignKey('communities.id' , ondelete='cascade'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    communities = db.relationship("Community", backref="posts")

    likes = db.relationship("Likes", backref="posts")

class Playlist(db.Model):

    __tablename__ = 'playlist'

    id = db.Column(db.Integer , primary_key=True)

    user_id = db.Column(db.Integer , db.ForeignKey('users.id', ondelete='cascade'))

    song_id = db.Column(db.Integer , db.ForeignKey('songs.id', ondelete='cascade'))


class Song(db.Model):

    __tablename__ = 'songs'

    id = db.Column(db.Integer , primary_key=True)

    artist = db.Column(db.Text, nullable=False)
    
    images = db.Column(db.Text , nullable=True, unique=True)

    title = db.Column(db.Text , nullable=False)

    link = db.Column(db.Text , nullable=False)

    user_id = db.Column(db.Integer , db.ForeignKey('users.id', ondelete='cascade'))

    
def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
    
