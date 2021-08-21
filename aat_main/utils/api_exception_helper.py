from flask import request, json
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    code = 404
    message = 'Not Found Exception'

    def __init__(self, code=None, message=None):
        if code:
            self.code = code
        if message:
            self.message = message
        super(APIException, self).__init__(message, None)

    def get_body(self, environ=None):
        body = dict(
            message=self.message,
            request=request.method + ' ' + self.get_url_no_param()
        )
        text = json.dumps(body)
        return text

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]


class Success(APIException):
    code = 200
    message = 'OK'


class BadRequestException(APIException):
    code = 400
    message = 'Bad Request Exception'


class UnauthorizedException(APIException):
    code = 401
    message = 'Unauthorized Exception'


class ForbiddenException(APIException):
    code = 403
    message = 'Forbidden Exception'


class NotFoundException(APIException):
    code = 404
    message = 'Not Found Exception'


class InterServerErrorException(APIException):
    code = 500
    message = 'Inter Server Error Exception'


class ServerUnavailableException(APIException):
    code = 503
    message = 'Server Unavailable Exception'
