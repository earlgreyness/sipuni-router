from flask import abort, request
from flask_restful import Api, Resource, reqparse

from router import app, db
from router.models import check_pair_exists, Operator, Record


class Router(Resource):
    def get(self, company, department):
        parser = reqparse.RequestParser()
        parser.add_argument('fromnum')
        parser.add_argument('tonum')
        parser.add_argument('dtmf')
        parser.add_argument('label')
        parser.add_argument('time')
        args = parser.parse_args()

        app.logger.info('Request to {}: {}'.format(request.path, args))
        record = Record(address=request.path, args=args)

        if not check_pair_exists(company, department):
            db.session.commit()
            abort(404)

        found = Operator.query.filter_by(
            department_name=department, phone_number=args['fromnum']
        ).first() is not None

        app.logger.info('Found: {}'.format(found))

        choice = int(found)
        record.choice = choice
        db.session.commit()
        return {'choice': choice}


api = Api(app)
api.add_resource(Router, '/<company>/<department>')
