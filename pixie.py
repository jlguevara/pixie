import pymysql
from flask import Flask, g, render_template, url_for, request, Response, jsonify

app = Flask(__name__)

conn = pymysql.connect(host='aa1pxnr8mnofxjk.cshd2j4rs3fz.us-west-1.rds.amazonaws.com',
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

@app.route('/', methods=['GET', 'POST'])
def show_posts():
    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        sql = "insert into posts (source, destination) values (%s, %s)"
        g.cur.execute(sql, (source, destination))
        g.cur.connection.commit()


    g.cur.execute("select * from posts")

    app.logger.error("after select")
    posts = [dict(source=row[0], destination=row[1])
            for row in g.cur.fetchall()]
    return render_template('show_posts.html', posts=posts)

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
            app.logger.warning('Lost connection to db in /posts, reconnecting...')
            if g.cur.connection.ping(True):
                g.cur.execute(sql)
            else:
                return 'database error'

        results = g.cur.fetchall()
        posts = [dict(id=row[0], start=row[1], end=row[2], day=str(row[3]), 
            driver_enum=row[4], time=row[5], user_id=row[6]) 
            for row in results]

        return jsonify({'posts': posts});

    else:
        return create_post()

def create_post():
    pass

if __name__ == '__main__':
    app.run(debug=False)

