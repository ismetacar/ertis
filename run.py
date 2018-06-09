import json
import traceback

from flask import Response

from src import create_app
from src.utils.errors import ErtisError
from src.utils.json_helpers import bson_to_json

app = create_app()


@app.errorhandler(Exception)
def handle_exceptions(error):
    if isinstance(error, ErtisError):
        response = {
            'err_msg': error.err_msg or 'Internal error occurred',
            'err_code': error.err_code or 'errors.internalError',
            'context': error.context,
            'reason': error.reason
        }
        status_code = error.status_code

    else:
        response = {
            'err_msg': str(error),
            'err_code': "errors.internalError",
            'traceback': str(traceback.extract_stack())
        }
        status_code = getattr(error, 'code', 500)

    return Response(
        json.dumps(response, default=bson_to_json), status_code,
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run()
