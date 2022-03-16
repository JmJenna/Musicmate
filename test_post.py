# """Post View tests."""
# import os
# from unittest import TestCase

# from models import db, connect_db, Post, User

# os.environ['DATABASE_URL'] = "postgresql:///spotify"

# from app import app, CURR_USER_KEY

# db.create_all()


app.config['WTF_CSRF_ENABLED'] = False


class PostViewTestCase(TestCase):
    """Test views for posts."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Post.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_post(self):
        """Can user add a post?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/posts/new", data={"title":"Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            post = Post.query.one()
            self.assertEqual(post.title, "Hello")