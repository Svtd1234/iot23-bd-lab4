import os
import re
import sqlite3
import tempfile

from my_project import create_app

DATA_SQL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.sql")


def mysql_to_sqlite(script):
    script = re.sub(r"CREATE DATABASE[^;]*;", "", script, flags=re.S)
    script = re.sub(r"USE\s+\w+;", "", script)
    script = re.sub(r"ENGINE\s*=\s*InnoDB", "", script)
    script = re.sub(r"(\w+)\s+(?:BIG)?INT\s+AUTO_INCREMENT\s+PRIMARY KEY", r"\1 INTEGER PRIMARY KEY AUTOINCREMENT", script)
    script = re.sub(r"UNIQUE KEY\s+\w+\s*\(", "UNIQUE (", script)
    script = re.sub(r"ENUM\([^)]*\)", "TEXT", script)
    return script


def build_sqlite(path):
    with open(DATA_SQL, encoding="utf-8") as f:
        script = mysql_to_sqlite(f.read())
    conn = sqlite3.connect(path)
    conn.executescript(script)
    conn.commit()
    conn.close()


def make_client():
    fd, path = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)
    build_sqlite(path)
    config = {"flask": {}, "database": {"driver": "sqlite", "sqlite_path": path}}
    app = create_app(config)
    app.testing = False
    return app.test_client(), path
