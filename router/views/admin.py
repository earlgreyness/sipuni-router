from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, logout_user, UserMixin, LoginManager
from flask_babelex import Babel
from flask import redirect, url_for, request, render_template

from router import app, db
from router.models import Company, Department, Operator, Record


ADMIN = UserMixin()
ADMIN.id = 'admin'

babel = Babel(app)  # for localization

login_manager = LoginManager(app)
login_manager.login_view = 'admin.login'


@app.route('/')
def the_index():
    return redirect(url_for('admin.index'))


@login_manager.user_loader
def load_user(user_id):
    if user_id == ADMIN.get_id():
        return ADMIN
    return None


class BaseView(ModelView):
    can_view_details = False
    create_modal = True
    edit_modal = True
    column_display_pk = True
    column_labels = {'name': 'Компания'}
    column_formatters = dict(
        date_created=lambda v, c, m, p: m.date_created.format('YYYY-MM-DD HH:mm:ss', locale='ru')
    )

    def get_column_name(self, field):
        if self.column_labels and field in self.column_labels:
            return self.column_labels[field]
        else:
            return str(field)

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for(login_manager.login_view))


class CompanyView(BaseView):
    form_columns = ['name']


class DepartmentView(BaseView):
    form_columns = ['company', 'name']
    column_labels = {'name': 'Отдел', 'company': 'Компания'}


class OperatorView(BaseView):
    column_display_pk = False
    column_labels = {
        'name': 'Имя',
        'department': 'Компания | отдел',
        'phone_number': 'Номер телефона',
    }


class RecordView(BaseView):
    can_delete = False
    can_edit = False
    can_create = False
    column_display_pk = False
    column_default_sort = ('date_created', True)  # descending order
    column_labels = {
        'date_created': 'Дата',
        'choice': 'Результат',
        'address': 'Запрос',
    }
    column_list = [
        'date_created',
        'address',
        'choice',
        'fromnum',
        'tonum',
        # 'dtmf',
        'label',
        # 'time',
    ]


class ProtectedAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login'))
        return super().index()

    @expose('/login', methods=['GET', 'POST'])
    def login(self):
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if (username == ADMIN.get_id()
                    and password == app.config['ADMIN_PASSWORD']):
                login_user(ADMIN, remember=True)

        if current_user.is_authenticated:
            return redirect(url_for('.index'))

        return render_template('login.html')

    @expose('/logout')
    def logout(self):
        logout_user()
        return redirect(url_for('.login'))


class CustomAdmin(Admin):
    def menu(self):
        """
            Removing Home menu entry.
        """
        return super().menu()[1:]


admin = CustomAdmin(
    app,
    template_mode='bootstrap3',
    name='SipuniRouter',
    index_view=ProtectedAdminIndexView(),
    base_template='admin_custom_index.html',
)
admin.add_view(CompanyView(Company, db.session, name='Компания'))
admin.add_view(DepartmentView(Department, db.session, name='Отдел'))
admin.add_view(OperatorView(Operator, db.session, name='Оператор'))
admin.add_view(RecordView(Record, db.session, name='Звонки'))
