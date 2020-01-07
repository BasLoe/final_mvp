from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mvp import db, login_manager, app
from flask_login import UserMixin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for, request
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask_login import login_user, current_user, logout_user, login_required

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#roles_users = db.table('roles_users',
 #                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
  #                     db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    strasse = db.Column(db.String(120), nullable=False)
    ansprechpartner = db.Column(db.String(120), nullable=False)
    plz = db.Column(db.Integer, nullable=False)
    ort = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(60), default='nothing')
    posts = db.relationship('Post', backref='author', lazy=True)
   #roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(100))
    typ = db.Column(db.String(120))
    bezahlung = db.Column(db.String(200))
    zeit = db.Column(db.String(120))

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class MyModelView(ModelView):


    def is_accessible(self):
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible:
            return redirect(url_for('home', next=request.url))

#class Role(db.Model):
 #   id = db.Column(db.Integer, primary_key=True)
  #  name = db.Column(db.String(40))
   # description = db.Column(db.String(255))

#user_datastore = SQLAlchemyUserDatastore(db, User, Role)
#security = Security(app, user_datastore)

admin = Admin(app)
admin.add_view(MyModelView(User, db.session, endpoint='testadmin'))
admin.add_view(MyModelView(Post, db.session))