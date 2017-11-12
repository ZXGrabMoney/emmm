from . import auth
from .. import dbdir,mail,httpauth
from flask import request,jsonify,current_app,session
from flask_mail import Message
import sqlite3
import random


@auth.route('/api/V1.0/user/register',methods=['POST'])
def api_register():
    args=request.get_json()
    print(args)
    if list(args.keys()) != ['mail','password','vertification_code']:
        return jsonify({'result':0})
    #if session.get('ver_code') is None or \
    #                session.get('ver_code')!=args['vertification_code']:
    #    return jsonify({'result':0})

    db=sqlite3.connect(dbdir)

    sql='select mail from users where mail="{}"'.format(args['mail'])
    if db.execute(sql).fetchone():
        db.close()
        return jsonify({'result':0})
    #hashed_pwd=httpauth.hash_password(args['password'])

    sql='insert into users(mail,password)values("{}","{}");'.format(args['mail'],args['password'])
    print(sql)
    db.execute(sql)
    db.commit()
    db.close()
    print(args.get('mail'))
    httpauth.login_user(args['mail'])

    return jsonify({'result':1})


@auth.route('/api/V1.0/user/send_mail',methods=['POST'])
def api_send_mail():
    print('mail...')
    args_dict = {}
    # args_dict['address']=request.args.get('address')
    # args_dict['content']=request.args.get('content')
    args_dict['mail'] = request.args.get('mail')

    db=sqlite3.connect(dbdir)
    sql='select mail from users where mail='+args_dict['mail']
    if not db.execute(sql).fetchone():
        return jsonify({'result':2})

    print(args_dict)
    msg = Message("验证码", sender=current_app.config['MAIL_USERNAME'], recipients=[args_dict.get('mail')])
    # print(args_dict['address'])
    # print(args_dict['content'])

    ver_code=random.randint(100000,999999)
    session['ver_code']=ver_code
    msg.body =str(ver_code)

    try:
        mail.send(msg)
        print('send successfully')
    except:
        session.pop('ver_code')
        return jsonify({'result': 0})

    return jsonify({'result': 1})

@auth.route('/api/V1.0/user/login',methods=['POST'])
def api_login():
    args = request.get_json()
    print(args)
    if list(args.keys()) != ['mail', 'password']:
        return jsonify({'result': 0})

    sql='select password from users where mail="{}"'.format(args['mail'])
    db=sqlite3.connect(dbdir)
    hashed_pwd=db.execute(sql).fetchone()[0]
    print(hashed_pwd)

    if not hashed_pwd:
        return jsonify({'result':0})
    if hashed_pwd!=args['password']:
        return jsonify({'result': 0})

    httpauth.login_user(args['mail'])
    db.close()

    return jsonify({'result': 1})


@auth.route('/api/V1.0/user/set_info',methods=['POST'])
@httpauth.login_required
def api_set_info():
    print("set_info....")
    mail=request.args.get('mail')
    if not mail:
        mail=session.get('mail')
    if not mail:
        mail=session.get('mail')
    if session.get('mail') != mail:
        return jsonify({"result":0})

    args = request.get_json()
    print(args)
    print(args.keys())
    keys=['name','school','grade','major','gender','good_at']
    if set(args.keys()) != set(keys):
        return jsonify({'result': 0})
    sql='update users set'
    db=sqlite3.connect(dbdir)
    for key in keys:
        sql+=' {}="{}",'.format(key,args[key])
    sql=sql[:-1]
    sql+=' where mail="{}"'.format(mail)
    print('selt_info')
    print(sql)
    db = sqlite3.connect(dbdir)
    db.execute(sql)
    db.commit()
    db.close()
    session['name']=args['name']
    return jsonify({'result':1})


@auth.route('/api/V1.0/user/get_info',methods=['GET'])
@httpauth.login_required
def api_get_info():
    name=request.args.get('name')
    if not name:
        name=session.get('name')
    if not name:
        return jsonify({'result':0})

    keys = ['name', 'school', 'grade', 'major', 'gender', 'good_at']

    sql='select name,school,grade,major,gender,good_at,connection from users where name="{}"'.format(name)
    print(sql)
    db=sqlite3.connect(dbdir)
    values=list(db.execute(sql).fetchone())
    re=dict(zip(keys,values))
    db.close()
    return jsonify(re)

@auth.route('/api/V1.0/user/get_pair_info',methods=["GET"])
@httpauth.login_required
def api_user_get_pair_info():
    name=request.args.get("name")
    if not name:
        name=session.get('name')
    if not name:
        return jsonify({"result":0})

    db=sqlite3.connect(dbdir)
    keys=['id','name','time','location','people_max','people_current','description','release_time']
    sql="select "
    for key in keys:
        sql+=key+","
    sql=sql[:-1]
    sql+=' from pairs where name="{}"'.format(name)
    print(sql)
    data=db.execute(sql).fetchall()
    print(data)
    re=[]
    for row in data:
        re.append(dict(zip(keys,list(row))))
    print(re)
    return jsonify(re)

