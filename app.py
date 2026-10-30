from my_project import create_app
from my_project.utils.config import load_config

config = load_config()
app = create_app(config)

if __name__ == "__main__":
    flask_cfg = config["flask"]
    app.run(
        host=flask_cfg.get("host", "0.0.0.0"),
        port=int(flask_cfg.get("port", 5000)),
        debug=bool(flask_cfg.get("debug", False)),
    )
