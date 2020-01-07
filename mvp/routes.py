import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from mvp import app, db, bcrypt, mail
from mvp.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from mvp.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message



@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/bt')
def bt():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(typ=1).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('bt.html', posts=posts)

@app.route('/mt')
def mt():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(typ=2).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('mt.html', posts=posts)

@app.route('/praktika')
def praktika():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(typ=4).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('praktika.html', posts=posts)

@app.route('/jobs')
def jobs():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(typ=3).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('jobs.html', posts=posts)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            flash('Login fehlgeschlagen. Bitte prüfen Sie ihre E-Mailadresse und ihr Passwort.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, strasse=form.strasse.data, ansprechpartner=form.ansprechpartner.data, plz=form.plz.data, ort=form.ort.data)
        db.session.add(user)
        db.session.commit()
        flash('Ihr Account wurde erstellt! Sie können sich jetzt einloggen.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/partner')
def partner():
    return render_template('partner.html')


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.strasse = form.strasse.data
        current_user.ansprechpartner = form.ansprechpartner.data
        current_user.plz = form.plz.data
        current_user.ort = form.ort.data
        db.session.commit()
        flash('Ihre Daten wurden aktualisiert!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.strasse.data = current_user.strasse
        form.ansprechpartner.data = current_user.ansprechpartner
        form.plz.data = current_user.plz
        form.ort.data = current_user.ort
    image_file = url_for('static', filename='pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, typ=form.typ.data , status='In Prüfung')
        db.session.add(post)
        db.session.commit()
        flash('Ihr Eintrag wurde erstellt und wird nun von einem Professor geprüft!', 'success')

        def send_post_email():
            post_msg = Message('Neuer Post')
            sender = 'startup.plattform@gmail.com',
            recipients = 'startup.plattform@gmail.com'
            msg.body = f''' Soeben wurde ein neuer Post auf der StartUp Plattform gepostet! Logge dich doch bitte in den Adminbereich ein und überprüfe den Beitrag.'''
            mail.send(post_msg)
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='Ausschreibung erstellen')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.typ = form.typ.data
        post.bezahlung = form.bezahlung.data
        post.zeit = form.zeit.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.typ.data = post.typ
        form.bezahlung.data = post.bezahlung
        form.zeit.data = post.zeit
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Eintrag korrigieren')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Ihr Eintrag wurde unwiderruflich gelöscht!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@app.route("/user/<string:username>")
@login_required
def my_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('my_posts.html', posts=posts, user=user)

@app.route("/fhw")
def fhw():
    return render_template('fhw.html')

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='startup.plattform@gmail.com',
                  recipients=[user.email])
    msg.body = f'''Um das Passwort zurückzusetzen, klicke bitte auf den nachfolgenden Link:
{url_for('reset_token', token=token, _external=True)}
Wenn du diese Anfrage nicht ausgelöst hast, kannst du diese E-Mail ignorieren, damit keine Veränderungen vorgenommen werden.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Soeben wurde eine E-Mail mit Informationen zum Zurücksetzen des Passwortes verschickt.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Dieser Link ist ungültig oder abgelaufen. Bitte fordere einen neuen Link an.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Dein Passwort wurde aktualisiert! Du kannst dich nun einloggen!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/loginadmin", methods=['GET', 'POST'])
def loginadmin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        role = User.query.filter_by(role='Administrator').first()
        if role and user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('testadmin.index_view'))
        else:
            flash('Login fehlgeschlagen. Sie haben nicht die entsprechenden Rechte, um auf diese Seite zuzugreifen. Bitte kontaktieren Sie den Administrator.', 'danger')
    return render_template('loginadmin.html', title='Login Admin', form=form)

@app.route("/abgeschlossene_projekte")
def abgeschlossene_projekte():
    return render_template('abgeschlossene_projekte.html')

@app.route("/trends")
def trends():
    return render_template('trends.html')