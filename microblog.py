from flask import Flask
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="postgres:///microblog"
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

def write_post(title, body):
    db.session.add(BlagPost(title, body, datetime.now()))
    db.session.commit()

def get_posts():
    return BlagPost.query.all()

def get_post(id):
    return BlagPost.query.filter_by(id=id).first()

if __name__ == "__main__":
    manager.run()