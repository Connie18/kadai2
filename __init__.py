import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    db_uri = os.environ.get('DATABASE_URL') or "postgresql://localhost/kadai2"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        # store the database in the instance folder
        # DATABASE=os.path.join(app.instance_path, 'kadai1.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # apply the blueprints to the app
    import blog, auth
    app.register_blueprint(blog.bp)
    app.register_blueprint(auth.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule('/', endpoint='index')

    return app


app = create_app()
db = SQLAlchemy(app)


# app.run(debug=True)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)


class TODO(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(80), unique=False, nullable=False)
    body = db.Column(db.String(120), unique=False, nullable=False)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=text('NOW()'))


class DONE(db.Model):
    __tablename__ = 'done'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(80), unique=False, nullable=False)
    body = db.Column(db.String(120), unique=False, nullable=False)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=text('NOW()'))
