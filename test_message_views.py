"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
# from collections import MutableMapping
from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database




# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
# with app.app_context():
#     db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    @classmethod
    def setUpClass(cls):
        os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
        with app.app_context():
            db.create_all()

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            User.query.delete()
            Message.query.delete()

            self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="testuser",
                                        image_url=None)

            db.session.commit()
            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with app.app_context():
            self.testuser = db.session.merge(self.testuser)
            with self.client as c:
                with c.session_transaction() as sess:
                    # testuser = User.query.get(self.testuser.id)
                    sess[CURR_USER_KEY] = self.testuser.id

                    # Now, that session setting is saved, so we can have
                    # the rest of ours test

                resp = c.post("/messages/new", data={"text": "Hello"})

                # Make sure it redirects
                self.assertEqual(resp.status_code, 302)

                msg = Message.query.one()
                self.assertEqual(msg.text, "Hello")

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.drop_all()
            db.session.commit()
