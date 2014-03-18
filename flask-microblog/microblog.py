from flask import Flask
from flask import request
from flask import session
from flask import redirect
from flask import render_template
from jinja2 import Template
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flaskext.bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="postgres:///microblog"
app.config['DEBUG'] = True
#i'm not going to keep my secret_key in a public github
try:
    secretfile = open("secret_key", "r")
    app.secret_key = secretfile.read()
    secretfile.close()
except IOError:
    print "WARNING: USING AN INSECURE KEY MEANT ONLY FOR TESTING PURPOSES"
    app.secret_key = """fhp9nap9p(*Y932uhl'po[]\\'p1'poi34["""
db = SQLAlchemy(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

bcrypt = Bcrypt(app)

#i know i should refactor all of my html into separate files,
#but that's a project for another day.
notloggedintemplate="""
<form id='loginform' name='loginform' method='post' action='login'>
    username:<input type='text' name='username' id='username'/>
    password:<input type='password' name='password' id='password' />
    <input type='submit' name='submit' id='submit' value='Submit'/>
</form>
<br/>"""
loggedintemplate="""
<form id='logoutform' name='logoutform' method='post' action='logout'>
    You are logged in as {{username}}
    <input type='submit' id='submit' name='submit' value='Logout'/>
</form><br/>
"""

class BlagPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(127), nullable=False)
    body = db.Column(db.UnicodeText)
    birthdate = db.Column(db.DateTime, nullable=False)
    authorid = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    def __init__(self, title, body, posttime, authorid):
        self.title = unicode(title)
        self.body = unicode(body)
        self.birthdate = posttime
        self.authorid = authorid

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(31), nullable=False, unique=True)
    password = db.Column(db.Unicode(127), nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column

    def __init__(self, catName):
        self.category=catName

def register_author(name, password):
    import pdb
    pdb.set_trace()
    pwdhash = bcrypt.generate_password_hash(password)
    db.session.add(Author(unicode(name), unicode(pwdhash)))
    db.session.commit()

def write_post(title, body, authorid):
    db.session.add(BlagPost(title, body, datetime.now(), authorid))
    db.session.commit()

def get_posts():
    return db.session.query(BlagPost, Author).join(Author).order_by(BlagPost.birthdate.desc()).all()

def get_post(id):
    q = db.session.query(BlagPost, Author).join(Author).filter(BlagPost.id==id)
    if q.count() != 0:
        return q.first()
    else:
        return None

@app.route('/')
def posts_view():
    myposts = get_posts()
    pagebody = """
                {% if myposts|length %}
                    {% for post in myposts %}
                        {{post.BlagPost.title}}<br/>
                        by {{post.Author.name}}<br/>
                        {{post.BlagPost.birthdate}}<br/><br/>
                    {% endfor %}
                {% else %}
                    No posts yet
                {% endif %}
                """
    if 'username' in session.keys():
        viewpage = Template(loggedintemplate+pagebody)
        return render_template(viewpage, myposts=myposts,
                               username=session['username'])
    else:
        viewpage = Template(notloggedintemplate+pagebody)
        return render_template(viewpage, myposts=myposts)

@app.route('/post/<int:postid>')
def post_view(postid):
    mypost = get_post(postid)
    renderargs = {}
    if mypost is not None:
        pagebody = """
                    {{mypost.BlagPost.title}}<br/>
                    by {{mypost.Author.name}}<br/>
                    {{mypost.BlagPost.birthdate}}<br/>
                    {{mypost.BlagPost.body}}<br/><br/>
                    """
        renderargs['mypost'] = mypost
    else:
        pagebody = "That post hasn't been written yet!"
    if 'username' in session.keys():
        viewpage = Template(loggedintemplate+pagebody)
        renderargs['username'] = session['username']
    else:
        viewpage = Template(notloggedintemplate+pagebody)
    return viewpage.render(**renderargs)

@app.route('/logout', methods=['POST'])
def logoutview():
    log_out()
    return redirect('/')

def log_out():
    session.clear()

@app.route('/login', methods=['POST'])
def loginview():
    pwd = request.form['password']
    username = request.form['username']
    return log_in(username, pwd)

def log_in(username, pwd):
    try:
        session['username'], session['userid']=get_user(username, pwd)
        return redirect('write')
    except AttributeError:
        return Template(notloggedintemplate+
            """Username or password was incorrect""").render()

def get_user(username, pwd):
    dbauthor = Author.query.filter_by(name=username).first()
    if bcrypt.check_password_hash(pwd, dbauthor.password):
        return username, dbauthor.id
    else:
        raise AttributeError

@app.route('/write', methods=['GET', 'POST'])
def write_view():
    if request.method == 'GET':
        #display the writing GUI
        pagebody = """
            <form id='blagform' name='blagform' method='post' action='write'>
                Title: <input type='text' name='blagtitle' id='blagtitle'/><br/>
                Body: <br/>
                <textarea name='blagbody' id='blagbody' rows='5' cols='100' placeholder='type your blag here'></textarea><br/>
                <input type='submit' name='submit' id='submit' value='Submit'/>
            </form>
            """
        if 'username' in session.keys():
            viewpage = Template(loggedintemplate+pagebody)
            return viewpage.render(username=session['username'])
        else:
            viewpage = Template(notloggedintemplate+
                """You are not logged in, please use the form above.
                """)
            return viewpage.render()
    elif request.method == 'POST':
        #put the post in the database, then load the blog view
        write_post(request.form['blagtitle'],
            request.form['blagbody'],
            session['userid'])
        return redirect('/')

if __name__ == "__main__":
    manager.run()