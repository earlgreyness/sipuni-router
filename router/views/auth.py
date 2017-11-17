from flask_login import (
    LoginManager, UserMixin, login_required, logout_user, login_user, current_user)
from flask import redirect, url_for, request, render_template

from router import app

login_manager = LoginManager(app)
login_manager.login_view = 'login'

admin = UserMixin()
admin.id = 'admin'


@login_manager.user_loader
def load_user(user_id):
    if user_id == admin.id:
        return admin
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == admin.id and password == app.config['ADMIN_PASSWORD']:
            login_user(admin, remember=True)

    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
