import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

class MessageModelTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        
        with app.app_context():
            # Create our tables (we do this here, so we only create the tables
            # once for all tests --- in each test, we'll delete the data
            # and create fresh new clean test data
            db.create_all()

            u = User(
                email="test@test.com",
                username="testuser",
                password="DONT_LOOK!!!"
            )
            
            db.session.add(u)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.drop_all()
            db.session.commit()

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

    def test_message_model(self):
        """Does the basic message model work?"""
        with app.app_context():
            u = User.query.filter(User.username == "testuser").first()
            m = Message(
                text = "test message",
                user_id = u.id
            )
            db.session.add(m)
            db.session.commit()
            self.assertEqual(len(u.messages), 1)
    
    def test_message_no_user(self):
        """Does the basic message model work?"""
        with app.app_context():
            m = Message(
                text = "test message",
                user_id = None
            )
            db.session.add(m)
            with self.assertRaises(IntegrityError): 
                db.session.commit()

    def test_message_invalid_user(self):
        """Does the basic message model work?"""
        with app.app_context():
            m = Message(
                text = "test message",
                user_id = 9999
            )
            db.session.add(m)
            with self.assertRaises(IntegrityError): 
                db.session.commit()

    