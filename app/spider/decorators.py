from functools import wraps


def retry_task(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        retry = kwargs.get('retry', False)

        if retry == 0:
            return f(*args, **kwargs)

        elif retry > 0:
            for x in range(0, retry):
                result = f(*args, **kwargs)
                if result['status'] != 500:
                    return result
            return f(*args, **kwargs)
        elif retry == -1:
            while retry:
                result = f(*args, **kwargs)
                if result['status'] != 500:
                    return result
    return decorated_function


