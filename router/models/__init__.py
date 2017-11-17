from functools import partial

from sqlalchemy import Column as BaseColumn, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from router import db

Column = partial(BaseColumn, nullable=False)


class Company(db.Model):
    name = Column(String, primary_key=True)

    def __str__(self):
        return self.name


class Department(db.Model):
    company_name = Column(String, ForeignKey('company.name'))
    name = Column(String, primary_key=True)

    company = relationship('Company', lazy='joined')

    def __str__(self):
        return '{} | {}'.format(self.company_name, self.name)


def check_pair_exists(company, department):
    d = Department.query.filter_by(name=department).first()
    if d is None:
        return False
    return d.company_name == company


class Operator(db.Model):
    id = Column(Integer, primary_key=True)
    department_name = Column(String, ForeignKey('department.name'))
    name = Column(String)
    phone_number = Column(String)

    department = relationship('Department', lazy='joined')

    def __str__(self):
        return self.name
