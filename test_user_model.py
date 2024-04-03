"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
# Now we can import app

from app import app


class UserModelTestCase(TestCase):
    """Test views for messages."""
    @classmethod
    def setUpClass(cls):
        
        with app.app_context():
            # Create our tables (we do this here, so we only create the tables
            # once for all tests --- in each test, we'll delete the data
            # and create fresh new clean test data
            db.create_all()

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            User.query.delete()
            Message.query.delete()
            Follows.query.delete()

            self.client = app.test_client()
            
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            # db.drop_all()
            db.session.commit()

    def test_user_model(self):
        """Does basic model work?"""
        with app.app_context():
            u = User(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()

            # User should have no messages & no followers
            self.assertEqual(len(u.messages), 0)
            self.assertEqual(len(u.followers), 0)

    def test_user_following_following(self):
        """test if is_following detects when a user is actually following another user"""
        with app.app_context():
            u1 = User(
                email="test1@test.com",
                username="testuser1",
                password="HASHED_PASSWORD"
            )
            u2 = User(
                email="test2@test.com",
                username="testuser2",
                password="DONT_LOOK!!!"
            )
            db.session.add(u1)
            db.session.add(u2)
            db.session.commit()

            f = Follows(
                user_being_followed_id = u1.id,
                user_following_id = u2.id
            )
            db.session.add(f)
            db.session.commit()

            #User1.is_followed_by User2 should be True
            self.assertEqual(u1.is_followed_by(u2),True)
            #User2.is_following User1 should be True
            self.assertEqual(u2.is_following(u1), True)

    def test_user_following_not_following(self):
        """test if is_following detects when a user is actually following another user"""
        with app.app_context():
            u1 = User(
                email="test3@test.com",
                username="testuser3",
                password="HASHED_PASSWORD"
            )
            u2 = User(
                email="test4@test.com",
                username="testuser4",
                password="DONT_LOOK!!!"
            )
            db.session.add(u1)
            db.session.add(u2)
            db.session.commit()

            #User1.is_followed_by User2 should be False
            self.assertEqual(u1.is_followed_by(u2),False)
            #User2.is_following User1 should be False
            self.assertEqual(u2.is_following(u1), False)

    def test_user_signup(self):
        with app.app_context():
            u = User.signup("signupTest","signupTest@test.com", "password", "/static/images/default-pic.png")
            # test to make sure that newly signed up user exists in the db
            self.assertEqual(User.query.filter(User.username == "signupTest").first(), u) 

    def test_user_signup_dup(self):
        with app.app_context():
            with self.assertRaises(IntegrityError):
                User.signup("testuser","signupTest@test.com", "password", "/static/images/default-pic.png")
                db.session.commit()

    def test_user_signup_dup_email(self):
        with app.app_context():
            with self.assertRaises(IntegrityError):
                User.signup("duptesting","test@test.com", "password", "/static/images/default-pic.png")
                db.session.commit()          

    def test_auth_success(self):
        with app.app_context():
            u = User.signup("testAuth","testAuth@test.com", "password", "/static/images/default-pic.png")
            self.assertEqual(User.authenticate("testAuth", "password"), u)

    def test_auth_bad_pw(self):
        with app.app_context():
            u = User.signup("testAuth2","testAuth2@test.com", "password", "/static/images/default-pic.png")
            self.assertFalse(User.authenticate("testAuth2", "password2"), u)

    def test_auth_bad_username(self):
        with app.app_context():
            u = User.signup("testAuth3","testAuth3@test.com", "password", "/static/images/default-pic.png")
            self.assertFalse(User.authenticate("testAuth99", "password"), u)

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.drop_all()
            db.session.commit()