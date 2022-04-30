import logging

from app import db
import os
from app.db.models import User, Song
from flask_login import login_user, login_required, logout_user, current_user
from faker import Faker
import pytest
from werkzeug.datastructures import FileStorage
import flask_login

def test_song_upload(client, application):
    log = logging.getLogger("myApp")

    with application.app_context():
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
        root = os.path.dirname(os.path.abspath(__file__))
        testFile = os.path.join(root, 'testfiles/music.csv')
        myfile = open(testFile,'r')
        token = str(client.get('/login').data)
        token = extract_csrf_token(token)
        # log.info(token)
        data = {
            'email':'test@njit.edu',
            'password': 'qwerty1234',
            'csrf_token': token
        }
        response = client.post('/login', data=data, follow_redirects=True)
        # log.info(response.data)
        token = str(client.get('/songs/upload').data)
        token = extract_csrf_token(token)
        # log.info('the token ' +token)
        # fileData = {
        #     'file':str(myfile),
        #     'csrf_token': token
        # }
        # response = client.post('/songs/upload', data=fileData, follow_redirects=True)
        my_files = FileStorage(
        stream=open(testFile, "rb"),
        filename="music.csv",
        content_type="multipart/form-data",
        )
        # data['file'] = str(myfile)
        # application.login()
        response = client.post(
        '/songs/upload', data={'file':my_files, 'csrf_token':token}, follow_redirects=True,
        content_type='multipart/form-data'
        )
        assert db.session.query(Song).count() == 457

def extract_csrf_token(page):
    start = page.find('name="csrf_token" type="hidden" value="')+len('name="csrf_token" type="hidden" value="')
    page = page[start:]
    end = page.find('"')
    page = page[:end]
    return page
