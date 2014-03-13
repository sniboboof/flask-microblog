import pdb
from flask import Flask
from jinja2 import Template
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="postgres:///microblog"
app.config['DEBUG'] = True
db = SQLAlchemy(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class BlagPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(127))
    body = db.Column(db.UnicodeText)
    birthdate = db.Column(db.DateTime)

    def __init__(self, title, body, posttime):
        self.title = unicode(title)
        self.body = unicode(body)
        self.birthdate = posttime

# class Author(db.Model):
#     pass

def write_post(title, body):
    db.session.add(BlagPost(title, body, datetime.now()))
    db.session.commit()

def get_posts():
    return BlagPost.query.order_by(BlagPost.birthdate.desc()).all()

def get_post(id):
    return BlagPost.query.filter_by(id=id).first()

@app.route('/')
def posts_view():
    myposts = get_posts()
    viewpage = Template("""
                        {% if myposts|length %}
                            {% for post in myposts %}
                                {{post.title}}<br/>{{post.birthdate}}<br/><br/>
                            {% endfor %}
                        {% else %}
                            No posts yet
                        {% endif %}
                        """)
    return viewpage.render(myposts=myposts)

@app.route('/post/<int:postid>')
def post_view(postid):
    mypost = get_post(postid)
    viewpage = Template("""
                        {{title}}<br/>{{birthdate}}<br/>
                        {{body}}<br/><br/>
                        """)
    try:
        return viewpage.render(title=mypost.title,
                               birthdate=mypost.birthdate,
                               body=mypost.body)
    except AttributeError:
        return Template("That post hasn't been written yet!").render()

@app.route('/write')
def write_view(body):
    pass

if __name__ == "__main__":
    manager.run()