from itertools import chain

from flask import abort, request, jsonify
from flask_restful import Api, Resource, reqparse
import arrow

from router import app, db
from router.models import check_pair_exists, Operator, Record, Event


def find(department, fromnum, *, moment):
    start = arrow.now().shift(minutes=-2)

    query_operators = Operator.query.filter_by(department_name=department)
    numbers = set(chain.from_iterable(x.get_numbers() for x in query_operators))

    query = Event.query.filter(
        Event.src_num == fromnum,
        Event.date_created > start,
        Event.date_created < moment,
    ).order_by(
        Event.date_created.desc()
    )

    found = False
    found_event = None

    for event in query:
        if event.short_dst_num in numbers:
            found = True
            found_event = event
            break

    return found, found_event


class Router(Resource):
    def get(self, company, department):
        finish = arrow.now()

        try:
            app.logger.debug(
                'Complete incoming info: path={}, args={}, form={}, json={}'
                .format(request.path, request.args, request.form, request.json)
            )
        except Exception:
            app.logger.exception('')

        parser = reqparse.RequestParser()
        parser.add_argument('fromnum')
        parser.add_argument('tonum')
        parser.add_argument('dtmf')
        parser.add_argument('label')
        parser.add_argument('time')
        args = parser.parse_args()

        app.logger.info('Request to {}: {}'.format(request.path, args))
        record = Record(address=request.path, args=args)
        db.session.add(record)

        if not check_pair_exists(company, department):
            db.session.commit()
            abort(404)

        fromnum = args['fromnum'] or ''
        found, event = find(department, fromnum, moment=finish)

        app.logger.info('Found: {}, event={!r}'.format(found, event))

        choice = int(found)

        record.choice = choice
        if event is not None:
            record.tonum = event.short_dst_num
        db.session.commit()

        return {'choice': choice}


@app.route('/events', methods=['GET', 'POST'])
def events():
    data = request.args.to_dict(flat=True)
    data.update(request.json or {})

    event = Event(data)
    db.session.add(event)
    db.session.commit()

    app.logger.debug('{!r} saved'.format(event))

    return jsonify(success=True)


api = Api(app)
api.add_resource(Router, '/<company>/<department>')
