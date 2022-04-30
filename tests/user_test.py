import logging
from flask import redirect
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.db.models import User, Song
from faker import Faker

def test_adding_user(application):
    log = logging.getLogger("myApp")
    with application.app_context():
        assert db.session.query(User).count() == 0
        assert db.session.query(Song).count() == 0
        #showing how to add a record
        #create a record
        user = User('keith@webizly.com', 'testtest')
        #add it to get ready to be committed
        db.session.add(user)
        #call the commit
        #db.session.commit()
        #assert that we now have a new user
        #assert db.session.query(User).count() == 1
        #finding one user record by email
        user = User.query.filter_by(email='keith@webizly.com').first()
        log.info(user)
        #asserting that the user retrieved is correct
        assert user.email == 'keith@webizly.com'
        #this is how you get a related record ready for insert
        user.songs= [Song("test","smap"),Song("test2","te")]
        #commit is what saves the songs
        db.session.commit()
        assert db.session.query(Song).count() == 2
        song1 = Song.query.filter_by(title='test').first()
        assert song1.title == "test"
        #changing the title of the song
        song1.title = "SuperSongTitle"
        #saving the new title of the song
        db.session.commit()
        song2 = Song.query.filter_by(title='SuperSongTitle').first()
        assert song2.title == "SuperSongTitle"
        #checking cascade delete
        db.session.delete(user)
        assert db.session.query(User).count() == 0
        assert db.session.query(Song).count() == 0


def test_user_regestration(client):
    assert db.session.query(User).count() == 0
    log = logging.getLogger("myApp")
    token = str(client.get('/register').data)
    start = token.find('name="csrf_token" type="hidden" value="')+len('name="csrf_token" type="hidden" value="')
    token = token[start:]
    end = token.find('"')
    token = token[:end]
    # log.info(token)
    data = {
        'email':'test@njit.edu',
        'password': 'qwerty1234',
        'confirm': 'qwerty1234',
        'csrf_token': token
    }
    response = client.post('/register', data=data)
    # log.info(response)
    user = User.query.filter_by(email='test@njit.edu').first()
    # log.info(user)
    assert user.email == 'test@njit.edu'
    assert db.session.query(User).count() == 1
    return user

def test_user_login(application, client):
    with application.app_context():
        token = str(client.get('/login').data)
        token = extract_csrf_token(token)
        # log.info(token)
        data = {
            'email':'test@njit.edu',
            'password': 'qwerty1234',
            'csrf_token': token
        }
        response = client.post('/login', data=data, follow_redirects=True)
        assert b'Welcome' in response.data


def test_user_login_access(application, client):
    with application.app_context():
        token = str(client.get('/login').data)
        token = extract_csrf_token(token)
        data = {
            'email':'test@njit.edu',
            'password': 'qwerty1234',
            'csrf_token': token
        }
        response = client.post('/login', data=data, follow_redirects=True)
        response = client.get('/users', follow_redirects=True)
        assert response.status_code == 200

def extract_csrf_token(page):
    start = page.find('name="csrf_token" type="hidden" value="')+len('name="csrf_token" type="hidden" value="')
    page = page[start:]
    end = page.find('"')
    page = page[:end]
    return page

