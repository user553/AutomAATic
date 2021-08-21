import logging

from aat_main import app as application

if __name__ == '__main__':
    application.run(debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)