import pymysql
from flask import Flask, g, render_template, url_for, request, Response, jsonify

app = Flask(__name__)

conn = pymysql.connect(host='rebootinstance.cshd2j4rs3fz.us-west-1.rds.amazonaws.com',
        port=3306,
        user='admin',
        passwd='pixie409',
        db='pixiedb');

@app.before_request
def before_request():
    g.cur = conn.cursor()

@app.teardown_request
def teardown_request(exception):
    cur = getattr(g, 'cur', None)
    if cur is not None:
        cur.close()

@app.route('/')
def index():
    body = """
    Welcome to the Pixie API.  We currently support 
    GET /users, GET /users/id,
    GET /posts, and POST /posts.
    """
    return body

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@app.route('/users', methods = ['GET', 'POST'])
def users():
    if request.method == 'GET':
        sql = "select id, name, age, email, gender, bio from users"
        try:
            g.cur.execute(sql)
        except pymysql.err.OperationalError:
            app.logger.warning('Lost connection to db in /users, reconnecting...')
            if g.cur.connection.ping(True):
                g.cur.execute(sql)
            else:
                return 'database error'

        results = g.cur.fetchall()
        users = [dict(id=row[0], name=row[1], age=row[2], email=row[3], 
            gender=row[4], bio=row[5]) 
            for row in results]

        return jsonify({'users': users});

    else:
        return create_user()

def create_user():
    pass

@app.route('/users/<userid>')
def user(userid):
   sql = "select id, name, age, email, gender, bio from users where id = %s" 
   try:
        g.cur.execute(sql, (userid)) 
   except:
        app.logger.warning('Lost connection to db in /users/id, reconnecting...')
        if g.cur.connection.ping(True):
            g.cur.execute(sql, (userid))
        else:
            return 'database error'

   row = g.cur.fetchone()
   if row:
       return jsonify({'id': row[0], 'name': row[1], 'age': row[2], 
           'email': row[3], 'gender': row[4], 'bio': row[5]}) 
   else:
       return not_found()
	

@app.route('/posts', methods = ['GET', 'POST'])
def posts():
    if request.method == 'GET':
        sql = "select * from posts"
        try:
            g.cur.execute(sql)
        except pymysql.err.OperationalError:
            app.logger.warning(
                    'Lost connection to db in /posts, reconnecting...')
            if g.cur.connection.ping(True):
                g.cur.execute(sql)
            else:
                return 'database error'

        results = g.cur.fetchall()
        posts = [dict(id=row[0], start=row[1], end=row[2], day=str(row[3]), 
            driverEnum=row[4], time=row[5], userId=row[6]) 
            for row in results]

        return jsonify({'posts': posts});

    else:
        return create_post()

def create_post():
    start = request.get_json().get('start', '')
    end = request.get_json().get('end', '')
    day = request.get_json().get('day', '')
    driver_enum = request.get_json().get('driverEnum', '')
    time = request.get_json().get('time', '')
    user_id = request.get_json().get('userId','')


    sql = 'insert into posts (start, end, day, driver_enum, time, user_id) \
            values (%s, %s, %s, %s, %s, %s)'
    try:
        g.cur.execute(sql, (start, end, day, driver_enum, time, user_id))
    except pymysql.err.OperationalError:
        app.logger.warning(
                'Lost connection to db in create_post, reconnecting...')
        if g.cur.connection.ping(True):
            g.cur.execute(sql, (start, end, day, driver_enum, time, user_id))
        else:
            return 'database error'

    g.cur.connection.commit()

    post_id = g.cur.lastrowid
    sql = "select * from posts where id = %s"
    try:
        g.cur.execute(sql, (post_id))
    except pymysql.err.OperationalError:
        app.logger.warning(
                'Lost connection to db in /posts, reconnecting...')
        if g.cur.connection.ping(True):
            g.cur.execute(sql, (post_id))
        else:
            return 'database error'

    row = g.cur.fetchone()
    return jsonify({'id': row[0], 'start': row[1], 'end': row[2], 
        'day': str(row[3]), 'driverEnum': row[4], 'time': row[5], 
        'userId': row[6]}) 



if __name__ == '__main__':
    app.run(debug=False)

