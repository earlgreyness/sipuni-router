import arrow

import router.utils
from router import db, app
from router.models import Event


@router.utils.context
def main():
    moment = arrow.now().shift(minutes=-7)
    query = Event.query.filter(Event.date_created < moment)
    total = query.count()
    for event in query:
        db.session.delete(event)
    db.session.commit()
    app.logger.info('Events deleted: {}'.format(total))


if __name__ == '__main__':
    main()
