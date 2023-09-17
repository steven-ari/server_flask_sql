import logging
from functools import wraps

from app import db, app

def success_or_404(func):
    @wraps(func)
    def wrapper_func(*sub, **kw):
        try:
            return func(*sub, **kw)
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return {"message": "Error occurred"}, 400
    return wrapper_func
