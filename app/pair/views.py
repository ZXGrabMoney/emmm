from . import pair
from .. import dbdir,mail,httpauth
from flask import request,jsonify,current_app,session,render_template
from flask_mail import Message
import sqlite3
import time


quick_pairs_pool={}
divided_pairs_pool={}

@pair.route('/api/V1.0/quick_pairs/release_pair',methods=['POST'])
@httpauth.login_required
def api_release_quick_pair():
    name=request.args.get('name')
    if not name:
        return jsonify({'result':0})

    args = request.get_json()
    keys=['location']
    if list(args.keys()) != keys:
        return jsonify({'result': 0})

    pair=dict(args)

    pair['time'] = time.strftime("%Y-%m-%d %X")
    pair['name']=name
    pair['result']=[]

    if pair['location'] not in divided_pairs_pool.keys():
        divided_pairs_pool['location']=[]
    if name not in divided_pairs_pool:
        divided_pairs_pool['location'].append(name)

    quick_pairs_pool[name]=pair

    return jsonify({'result':1})

@pair.route('/api/V1.0/quick_pairs/get_users',methods=['GET'])
@httpauth.login_required
def api_get_users():
    name = request.args.get('name')
    if not name or quick_pairs_pool.get(name) is None\
            or quick_pairs_pool['name'].get('result') == []:
        return jsonify({'result': 0})

    if len(quick_pairs_pool[name]['result']) <4:
        return jsonify({'result': 0})
    print(name+"request quick_pair result")

    keys = ['name', 'school', 'grade', 'major','gender',
            'good_at', 'description', 'connection','icon_url']

    db = sqlite3.connect(dbdir)

    re=[]
    for i in quick_pairs_pool[name].get('result'):
        sql = 'select name,school,grade,major,gender,good_at,' \
              'description,connection,icon_url from users ' \
              'where name=' + i
        values = list(db.execute(sql).fetchone())
        re.append(dict(zip(keys, values)))

    db.close()
    print(re)

    return jsonify(re)

def asnyc_pairing():
    while(True):
        for loc,name_list in divided_pairs_pool.items():
            if len(name_list)<4:
                continue
            for name in name_list[:4]:
                quick_pairs_pool[name]['result']=name_list[:4]
            divided_pairs_pool[loc]=name_list[4:]
        time.sleep(5)

@pair.route('/api/V1.0/quick_pairs/send_result',methods=['POST'])
@httpauth.login_required
def api_send_result():
    name = request.args.get('name')
    if not name:
        return jsonify({'result': 0})

    result = request.args.get('result')
    if not result:
        return jsonify({'result': 0})

    if int(result)==1:
        quick_pairs_pool.pop(name)
    else:
        divided_pairs_pool[quick_pairs_pool[name]['location']].append(name)

    db = sqlite3.connect(dbdir)
    sql = 'insert into quick_pairs(name,time,status)' \
          'values("{}","{}","{}")'.format(pair['name'],
                                          pair['time'],
                                          pair['status'])
    try:
        db.execute(sql)
    except:
        pass
    db.close()

    return jsonify({'result':1})

@pair.route('/api/V1.0/pairs/release_pair',methods=['POST'])
@httpauth.login_required
def api_release_pair():
    name = request.args.get('name')
    if not name:
        name=session.get('name')
    print(name)
    if not name:
        return jsonify({'result': 0})

    args = request.get_json()
    keys = ['time', 'location', 'people_max','description']
    print(args)
    if list(args.keys()) != keys:
        return jsonify({'result': 0})

    db=sqlite3.connect(dbdir)

    sql='insert into pairs(name,time,location,people_max,description,release_time,people_current,applicant)' \
        'values("{}","{}","{}","{}","{}","{}",{},"{}")'\
        .format(name,args['time'],args['location'],args['people_max'],
                args['description'],time.strftime("%Y-%m-%d %H:%M"),0,name)
    db.execute(sql)
    db.commit()
    db.close()

    return jsonify({'result': 1})

@pair.route('/api/V1.0/pairs/get_pairs',methods=['GET'])
@httpauth.login_required
def api_get_pairs():
    sql='select id, name,time,location,people_max,people_current,description,release_time from pairs'
    type=request.args.get('type')
    if type:
        sql=sql+' where type='+type
    db=sqlite3.connect(dbdir)
    data=db.execute(sql).fetchall()
    re=[]
    keys=['id','name','time','location','people_max','people_current','description','release_time']
    for row in data:
        re.append(dict(zip(keys,list(row))))
    return jsonify(re)

@pair.route('/api/V1.0/pairs/get_pair',methods=['GET'])
@httpauth.login_required
def api_get_pair():
    id=request.args.get('id')
    if not id:
        return {'result':0}
    sql='select id, name,time,location,people_max,people_current,description,release_time ' \
        'from pairs where id='+id
    print(sql)
    db=sqlite3.connect(dbdir)
    data=list(db.execute(sql).fetchone())
    keys=['id','name','time','location','people_max','people_current','description','release_time']
    re=dict(zip(keys,data))
    print(re)
    return jsonify(re)

@pair.route('/api/V1.0/pairs/get_users',methods=['GET'])
@httpauth.login_required
def api_get_users_1():
    id = request.args.get('id')
    if not id :
        return jsonify({'result':0})

    db = sqlite3.connect(dbdir)
    data=list(db.execute('select name,applicant from pairs '
                         'where id='+id).fetchone())
    print(data)
    if data[0]!=session.get('name'):
        db.close()
        return jsonify({'result':0})

    keys = ['name', 'school', 'grade', 'major', 'gender',
            'good_at']

    re=[]

    for i in list(data[1].split()):
        sql = 'select name,school,grade,major,gender,good_at,' \
              'description from users ' \
              'where name="{}"'.format(i)
        values = list(db.execute(sql).fetchone())
        re.append(dict(zip(keys, values)))

    db.close()
    print(re)

    return jsonify(re)

@pair.route('/api/V1.0/pairs/send_result',methods=['POST'])
@httpauth.login_required
def api_send_result_1():
    id = request.args.get('id')
    if not id:
        return jsonify({'result': 0})

    keys=['applicant_name','result']
    args=request.get_json()
    if list(args.keys())!=keys:
        return jsonify({'result': 0})

    db=sqlite3.connect(dbdir)

    sql='select name,applicants,agreed_persons from pairs ' \
        'where id='+id
    data=list(db.execute(sql).fetchone())

    if data[0]!=session.get('name'):
        db.close()
        return jsonify({'result':0})

    changed_applicants=data[1].strip(args['applicant_name'])
    sql="update pairs set applicants={} where id={}"\
        .format(changed_applicants,id)
    db.execute(sql)

    if args['result']==1:
        changed=data[2]+' '+args['applicant_name']
        sql = "update pairs set agreed_persons={} " \
              "where id={}".format(changed, id)
        db.execute(sql)

    db.close()

    return jsonify({'result': 1})

@pair.route('/api/V1.0/pairs/apply',methods=['POST'])
@httpauth.login_required
def api_apply():
    id = request.args.get('id')
    applicant_name=request.args.get('applicant_name')
    if not applicant_name:
        applicant_name=session.get('name')
    if not applicant_name:
        applicant_name=session.get('name')
    if not id or not applicant_name:
        return jsonify({'result': 0})

    print('apply.....')
    print(applicant_name)

    db = sqlite3.connect(dbdir)

    sql = 'select name,applicant,people_current,people_max from pairs ' \
          'where id=' + id
    print(sql)
    data = list(db.execute(sql).fetchone())

    if data[2]>=data[3]:
        return jsonify({'result':2})

    if applicant_name in data[1].split():
        return jsonify({'result':1})

    changed_applicants =data[1]+" "+applicant_name
    changed_curent=1
    if not data[2]:
        data[2]=1
    else:
        changed_curent=data[2]+1

    sql = 'update pairs set applicant="{}",people_current={} where id={}'\
        .format(changed_applicants,changed_curent, id)
    db.execute(sql)

    db.commit()

    db.close()

    return jsonify({'result': 1})

@pair.route('/viewingPage',methods=['GET'])
@httpauth.login_required
def viewingPage():
    return render_template('viewingPage.html')

@pair.route('/detail',methods=['GET'])
@httpauth.login_required
def detail():
    return render_template('detail.html')

@pair.route('/info',methods=['GET'])
@httpauth.login_required
def info():
    return render_template('info.html')

@pair.route('/navTemplates.html',methods=['GET'])
def nav():
    return render_template('navTemplates.html')

@pair.route('/signIn',methods=['GET'])
def signIn():
    return render_template('signIn.html')

@pair.route('/signUp1',methods=['GET'])
def signUp1():
    return render_template('signUp1.html')

@pair.route('/signUp2',methods=['GET'])
@httpauth.login_required
def signUp2():
    return render_template('signUp2.html')

@pair.route('/userHome',methods=['GET'])
@httpauth.login_required
def userHome():
    return render_template('userHome.html')