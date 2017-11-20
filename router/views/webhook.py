from flask import abort
from flask_restful import Api, Resource, reqparse

from router import app
from router.models import check_pair_exists, Operator


class Router(Resource):
    def get(self, company, department):
        parser = reqparse.RequestParser()
        parser.add_argument('fromnum')
        parser.add_argument('tonum')
        parser.add_argument('dtmf')
        parser.add_argument('label')
        parser.add_argument('time')
        args = parser.parse_args()

        app.logger.info('Request to /{}/{}: {}'.format(company, department, args))

        if not check_pair_exists(company, department):
            abort(404)

        variants = [args['fromnum'], args['tonum']]
        found = Operator.query.filter(
            Operator.department_name == department,
            Operator.phone_number.in_(variants)).first() is not None

        return {'choice': int(found)}


api = Api(app)
api.add_resource(Router, '/<company>/<department>')
