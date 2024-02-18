from flask import Flask, g
import os
from dotenv import load_dotenv
load_dotenv()


def create_app():
    app = Flask(__name__)
    
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.teardown_appcontext
    def teardown_db(exception=None):
        db = g.pop('db', None)
        if db is not None:
            # Close DB connection or perform any cleanup
            db.close()
    
    return app
