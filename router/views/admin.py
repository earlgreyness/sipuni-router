from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for

from router import app, db
from router.models import Company, Department, Operator


class BaseView(ModelView):
    column_display_pk = True
    column_labels = {'name': 'Компания'}

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


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


class CustomAdmin(Admin):
    def menu(self):
        """
            Removing Home menu entry.
        """
        return super().menu()[1:]


admin = CustomAdmin(app, template_mode='bootstrap3')
admin.add_view(CompanyView(Company, db.session, name='Компания'))
admin.add_view(DepartmentView(Department, db.session, name='Отдел'))
admin.add_view(OperatorView(Operator, db.session, name='Оператор'))
