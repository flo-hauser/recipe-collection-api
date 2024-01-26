from functools import wraps
from flask import request
from app.api.errors import bad_request

def required_fields(required_keys):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      data = request.get_json()
      if not data:
        return bad_request("No JSON body provided")
      for key in required_keys:
        if key not in data or not data[key]:
          return bad_request(f"Missing required field: {key}")
      return f(*args, **kwargs)
    return decorated_function
  return decorator


def required_query_params(required_keys):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      for key in required_keys:
        if key not in request.args:
          return bad_request(f"Missing required query parameter: {key}")
      return f(*args, **kwargs)
    return decorated_function
  return decorator