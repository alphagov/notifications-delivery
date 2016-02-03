from flask import jsonify, Blueprint


status = Blueprint('status', __name__)


@status.route('/_status')
def get_status():
    return jsonify(
        status="ok",
    ), 200
