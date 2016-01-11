from flask import jsonify

from app.main import main


@main.app_errorhandler(404)
def page_not_found(e):
    return jsonify(error=e.description or "Not found"), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    # TODO: log the error
    return jsonify(error="Internal error"), 500
