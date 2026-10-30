import os

from flask import Flask, jsonify, send_from_directory
from werkzeug.exceptions import HTTPException

from my_project.solar.route import create_api_blueprint
from my_project.utils.config import load_config
from my_project.utils.db import commit_db, get_db, rollback_db
from my_project.utils.errors import AppError
from my_project.utils.json_provider import AppJSONProvider

UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")


def create_app(config=None):
    app = Flask(__name__)
    app.json = AppJSONProvider(app)
    app.config["APP_CONFIG"] = config if config is not None else load_config()

    app.register_blueprint(create_api_blueprint())

    @app.get("/")
    def index():
        return send_from_directory(UI_DIR, "index.html")

    @app.get("/api/health")
    def health():
        get_db().fetch_one("SELECT 1 AS ok")
        return jsonify({"status": "ok"}), 200

    @app.get("/api/routes")
    def routes():
        rules = []
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
            if rule.rule.startswith("/api") and rule.rule != "/api/routes":
                methods = sorted(m for m in rule.methods if m not in ("HEAD", "OPTIONS"))
                rules.append({"url": rule.rule, "methods": methods})
        return jsonify(rules), 200

    @app.after_request
    def finish_transaction(response):
        if response.status_code < 400:
            commit_db()
        else:
            rollback_db()
        return response

    @app.teardown_request
    def cleanup(exc):
        if exc is not None:
            rollback_db()

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify(error.to_dto()), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": error.name, "message": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        app.logger.exception("Необроблена помилка")
        return jsonify({"error": "InternalServerError", "message": "Внутрішня помилка сервера"}), 500

    return app
