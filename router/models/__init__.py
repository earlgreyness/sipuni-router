from functools import partial

from sqlalchemy import Column as BaseColumn, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ArrowType
import arrow

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

    def get_numbers(self):
        return [x.strip() for x in (self.phone_number or '').split(',')]


class Record(db.Model):
    id = Column(Integer, primary_key=True)
    date_created = Column(ArrowType(timezone=True), default=arrow.now)

    fromnum = Column(String, default='')
    tonum = Column(String, default='')
    dtmf = Column(String, default='')
    label = Column(String, default='')
    time = Column(String, default='')

    address = Column(String, default='')
    choice = Column(Integer, nullable=True)

    def __init__(self, *, address, args, choice=None):
        self.address = address
        self.choice = choice

        for param in ['fromnum', 'tonum', 'dtmf', 'label', 'time']:
            setattr(self, param, args.get(param, '') or '')

    def __repr__(self):
        return '<Record({!r}, {!r})>'.format(self.address, self.result)
