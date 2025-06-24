import os

from flask import Flask
from .db import close_connection

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE="dbname=rentals user=postgres password=Zaq12wsx"
    )

    app.teardown_appcontext(close_connection)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .app import regiset_routes
    regiset_routes(app)

    return app
