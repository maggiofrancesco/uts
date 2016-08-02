# -*- coding: utf-8 -*-

import sys
import check_thread
from flask import Flask
from logbook import Logger, StreamHandler


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == "__main__":

    """
    The main entry point of the application
    """

    StreamHandler(sys.stdout).push_application()
    log = Logger('Main - Urban Transport System')

    log.notice("Flask server started.")
    check_thread.main()
    log.notice("Control Thread started.")

    app.run(debug=False)
