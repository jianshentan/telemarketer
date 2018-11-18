import os
from flask import Flask, jsonify
from .twilio import twilio
from .blob import blob
from .routes import bp
import json


def create_app(
    package_name=__name__,
    static_folder="static",
    template_folder="templates",
    **config_overrides
):

    # initialize app
    app = Flask(
        package_name,
        static_url_path="/assets",
        static_folder=static_folder,
        template_folder=template_folder,
    )
    
    # Account SID and Auth Token from www.twilio.com/console
    twilio.set_credentials(
        os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN")
    )

    # Add storage auth
    blob.create_block_blob_service(
        os.getenv("STORAGE_ACCOUNT_NAME"), os.getenv("STORAGE_ACCOUNT_KEY")
    )

    # create history file
    history = {}
    history_file = blob.get_file_name()
    with open(history_file, 'w') as outfile:  
        json.dump(history, outfile)


    # Apply overrides
    app.config.update(config_overrides)

    # Register Routes in routes.py
    app.register_blueprint(bp)

    return app
