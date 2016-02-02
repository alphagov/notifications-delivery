from flask import jsonify


def bad_request(e):
    return jsonify(error=str(e.description)), 400


def not_found(e):
    return jsonify(error=e.description or "Not found"), 404


def internal_server_error(e):
    return jsonify(error="Internal error"), 500
