from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

with app.app_context():
    db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):

    def setUp(self):
        """Create test users"""
        with app.app_context():
            db.drop_all()
            db.create_all()

            self.client = app.test_client()

            self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="testuser",
                                        image_url=None)
            self.testuser_id = 123
            self.testuser.id = self.testuser_id

            self.u1 = User.signup("test1", "test1@test.com", "password", None)
            self.u1_id = 234
            self.u1.id = self.u1_id
            self.u2 = User.signup("test2", "test2@test.com", "password", None)
            self.u2_id = 345
            self.u2.id = self.u2_id
            self.u3 = User.signup("test3", "test3@test.com", "password", None)
            self.u4 = User.signup("test4", "test4@test.com", "password", None)

            db.session.commit()

    def tearDown(self):
        with app.app_context():
            resp = super().tearDown()
            db.session.rollback()
            return resp
        
    def display_users(self):
        with app.app_context():
            with self.client as c:
                resp = c.get(f"/users/{self.testuser_id}")

                self.assertEqual(resp.status_code, 200)

                self.assertIn("@testuser", str(resp.data))

    def test_add_like(self):
        with app.app_context():
            m = Message(id=123, text="Like this message!", user_id=self.u1_id)
            db.session.add(m)
            db.session.commit()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser_id

                resp = c.post("/users/add_like/123", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                likes = Likes.query.filter(Likes.message_id == 123).all()
                self.assertEqual(len(likes), 1)
                self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_unauth_like(self):
        with app.app_context():
            
            msg = Message(id=999, text="Don't like me, I don't know you!", user_id=self.testuser_id)
            db.session.add(msg)
            db.session.commit()
            
            like = Likes(user_id=123, message_id=999)

            self.assertIsNotNone(msg)

            like_count = Likes.query.count()

            with self.client as c:
                resp = c.post(f"/users/add_like/{msg.id}", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                self.assertIn("Access unauthorized", str(resp.data))

                # The number of likes has not changed since making the request
                self.assertEqual(like_count, Likes.query.count())