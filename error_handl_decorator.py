class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def error_handling_decorator(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CustomError as ce:
            return str(ce)
        except Exception as not_handled_error:
            return f'error {type(not_handled_error)=} occured, please try again'
    return inner