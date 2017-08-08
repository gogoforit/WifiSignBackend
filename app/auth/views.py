from flask import current_app
from flask import jsonify
from flask import session
from .forms import LoginForm, RegistrationForm
from flask import render_template, request, render_template, redirect, url_for, flash
from flask.ext.principal import identity_changed, AnonymousIdentity, Identity
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from app.utils import response_dict
from app.models.BaseUser import User
from app.models.UserTemp import UserTemp
from app.constants import EMAIL_USED, NICKNAME_USED, SUCCESS, FORM_INVALID, LOGIN_FAIL, constants
from . import auth as auth_Blueprint



@auth_Blueprint.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth_Blueprint.route('/')
@login_required
def index():
    return render_template('index.html')


@auth_Blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate:
            if form.validate_email(request.form['email']):
                flash(EMAIL_USED)
                return render_template('login.html')
            elif form.validate_nickname(request.form['nickname']):
                flash(constants[NICKNAME_USED])
                return render_template('login.html')
            else:
                user = User(email=request.form['email'],
                            username=request.form['username'],
                            class_id=request.form['class_id'],
                            nickname=request.form['nickname'])
                user.password = request.form['password']
                user.save()
                flash(constants[SUCCESS])
                return render_template('login.html')
        else:
            flash(constants[FORM_INVALID])
            return render_template('login.html')
    else:
        return render_template('login.html')


@auth_Blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form['email'])
        user = User.objects(email=request.form['email']).first()
        if user is not None and user.verify_password(request.form['password']):
            print(user)
            login_user(user, remember=True)
            return redirect(url_for('auth.index'))
        else:
            flash(constants[LOGIN_FAIL])
            return render_template('login.html')
    else:
        return render_template('login.html')


@auth_Blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    return jsonify(response_dict(SUCCESS))


