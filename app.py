"""Blogly application."""
from flask import Flask, request, redirect, render_template
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

@app.route('/')
def homepage():
    """Shows all users"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('homepage.html', users=users)

@app.route('/addNewUser')
def newUser():
    """Directs to add user page"""
    return render_template('newUser.html')

@app.route('/addedUser', methods=['POST'])
def addedUser():
    """Adds new user"""
    new_user = User(
        first_name=request.form['first'],
        last_name=request.form['last'],
        image_url=request.form['image'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect('/')

@app.route('/editUser/<int:user_id>')
def editUser(user_id):
    """Edits a user by requesting a value from 0 to # of users. Then passes that value and to editUser.html to request the correct information."""

    # user = User.query.order_by(User.last_name, User.first_name).all()[int(id) - 1]
    user = User.query.get_or_404(user_id)

    return render_template('editUser.html', user=user)

@app.route('/commit/<int:user_id>')
def commitChanges(user_id):
    """Commits the changes made in editUser.html"""
    # changedUser = User.query.order_by(User.last_name, User.first_name).all()[int(id) - 1]
    changedUser = User.query.get_or_404(int(user_id))
    changedUser.first_name = request.args['first']
    changedUser.last_name = request.args['last']
    changedUser.image_url = request.args['image']

    db.session.add(changedUser)
    db.session.commit()

    return redirect('/')

@app.route('/user/<int:user_id>')
def user(user_id):
    """Route to user interface"""

    user = User.query.get_or_404(int(user_id))

    return render_template('user.html', user=user)

@app.route('/user/<int:user_id>/delete')
def deleteUserCheck(user_id):
    user = User.query.get_or_404(int(user_id))

    return render_template('deleteUser.html', user=user)

@app.route('/user/<int:user_id>/delete', methods=['POST'])
def deleteUser(user_id):
    user = User.query.get_or_404(int(user_id))

    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.full_name} deleted.")

    return redirect("/")

@app.route('/posts')
def showAllPosts():
    """Shows all posts in the data base"""

    posts = Post.query.all()

    return render_template('posts.html', posts=posts)

@app.route('/newPost/<user_id>')
def newPost(user_id):
    """Route to new post page"""

    user = User.query.get_or_404(int(user_id))

    return render_template('newPost.html', user=user)

@app.route('/addNewPost/<user_id>', methods=['POST'])
def addNewPost(user_id):
    """Route to add a new post"""

    newPost = Post(
        title = request.form['title'],
        comment = request.form['comment'],
        posted_by = int(user_id)
    )

    db.session.add(newPost)
    db.session.commit()

    return redirect('/')

@app.route('/editPost/<user_id>/<post_id>')
def editPost(user_id, post_id):
    """Route to edit a post. Takes both user id and post id so that when the post is edited the user can be redirected to their own user page."""

    user = User.query.get_or_404(int(user_id))
    post = Post.query.get_or_404(int(post_id))

    return render_template('editPost.html', user = user, post = post)

@app.route('/commitPostEdit/<user_id>/<post_id>', methods=['POST'])
def commitChange(user_id, post_id):
    """Commits the changes made on editPost.html and then redirects the user back to their own user page"""

    user = User.query.get_or_404(int(user_id))

    post = Post.query.get_or_404(int(post_id))

    post.title = request.form['title']
    post.comment = request.form['comment']

    db.session.add(post)
    db.session.commit()

    return redirect(f'/user/{post.posted_by}')

@app.route('/posts/<int:post_id>/delete')
def deletePostCheck(post_id):
    post = Post.query.get_or_404(int(post_id))

    return render_template('deletePost.html', post=post)

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def deletePost(post_id):
    post = Post.query.get_or_404(int(post_id))

    db.session.delete(post)
    db.session.commit()
    flash(f"Post {post.title} deleted.")

    return redirect(f"/user/{post.posted_by}")

@app.route('/tags')
def showAllTags():
    """Takes users to a page with all the tags"""
    tags = Tag.query.all()

    return render_template('tags.html', tags=tags)

@app.route('/tags/new')
def newTag():
    """Takes user to new tag page"""
    posts = Post.query.all()
    return render_template('newTag.html', posts=posts)

@app.route('/tags/new', methods=['POST'])
def addTag():
    """Actually adds the new tag being made"""
    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    newTag = Tag(name=request.form['name'], posts=posts)

    db.session.add(newTag)
    db.session.commit()

    return redirect("/tags")

@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    """Takes user to a page with info on a specific tag"""

    users = User.query.all()
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag.html', tag=tag, users=users)

@app.route('/tags/<int:tag_id>/edit')
def editTag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    post_ids = []
    for post in tag.posts:
        post_ids.append(post.id)

    return render_template('editTag.html', tag=tag, posts=posts, post_ids=post_ids)

@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def commitTag(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    tag.name = request.form['tagName']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()

    return redirect(f'/tags/{tag.id}')

@app.route('/tags/<int:tag_id>/delete')
def deleteTagCheck(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    return render_template('deleteTag.html', tag=tag)

@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def deleteTag(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    db.session.delete(tag)
    db.session.commit()
    flash(f"Post {tag.name} deleted.")

    return redirect('/tags')