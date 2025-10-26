import os

if os.getenv('CELERY_MODE') == 'True':
    import gevent.monkey
    gevent.monkey.patch_all()

from .celery import app as celery_app

__all__ = ('celery_app',)
