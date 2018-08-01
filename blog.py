from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    """Show all the posts, most recent first."""
    from __init__ import TODO, DONE
    todo = TODO.query.all()
    done = DONE.query.all()

    return render_template('blog/index.html', todos=todo, dones=done)


def get_todo(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    todo = get_db().session.query(g.TODO).filter_by(id=id)\
        .join(g.User, g.User.id == g.TODO.author_id).first()

    if todo is None:
        abort(404, "TODO id {0} doesn't exist.".format(id))

    if check_author and todo.author_id != g.user.id:
        abort(403)

    return todo


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            todo = g.TODO(title=title, body=body, author_id=g.user.id)
            db.session.add(todo)
            db.session.commit()

            flash('New task registered.')

            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    todo = get_todo(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            todo.title = title
            todo.body = body
            db.session.add(todo)
            db.session.commit()

            flash('Task updated.')

            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', todo=todo)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    todo = get_todo(id)
    db = get_db()
    db.session.delete(todo)
    db.session.commit()

    return redirect(url_for('blog.index'))
