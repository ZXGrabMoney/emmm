from functools import wraps
from flask import session,jsonify,abort,redirect,url_for
import hashlib
import sqlite3
#from . import dbdir

import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

dbdir=os.path.join(basedir,'data.db')
print(dbdir)

class HttpAuth(object):
    '''
    用户认证相关
    '''
    def login_required(self,f):
        @wraps(f)
        def decorated(*args, **kwargs):
            print('check login status')
            if session.get('mail'):
                print(session.get('name'))
                return f(*args, **kwargs)
            else:
                print(session.get('mail'))
                print('has not login')
                return redirect(url_for("pair.signIn"))
        return decorated

    def login_user(self,mail):
        print('login。。。。')

        session['mail']=mail
        db=sqlite3.connect(dbdir)
        name=db.execute('select name from users where mail="{}"'.format(mail)).fetchone()[0]
        print(name)
        session['name']=name
        db.close()

    def hash_password(self,password):
        return hashlib.sha256(password.encode('utf-8'))


