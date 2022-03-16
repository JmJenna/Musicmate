from app import db
from models import Community


db.drop_all()
db.create_all()

genres = [
    Community(genre="ART POP"),
    Community(genre="DANCE"),
    Community(genre="HIP-HOP"),
    Community(genre="K-POP"),
    Community(genre="R&B"),
    Community(genre="COUNTRY"),
    Community(genre="JAZZ"),
    Community(genre="ROCK&ROLL"),
]

db.session.add_all(genres)
db.session.commit()


