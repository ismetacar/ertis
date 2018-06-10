from flask import Response

from src.utils.errors import ErtisError


def ensure_db_is_available(generic_service):
    try:
        generic_service.find_one_by(collection='healtcheck')
    except Exception as e:
        raise ErtisError(
            err_msg="Ertis DB is not available",
            err_code="errors.dbConnectionError",
            status_code=500,
            context={
                'message': str(e)
            }
        )


def init_api(app, settings):
    @app.route('/api/{}/healtcheck'.format(settings['api_version']), methods=['GET'])
    def healtcheck():
        ensure_db_is_available(app.generic_service)

        return Response(status=200)
