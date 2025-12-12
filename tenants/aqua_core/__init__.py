# AquaERP Core Package

# هذا يضمن أن Celery يتم تحميله عند بدء Django
from .celery import app as celery_app

__all__ = ('celery_app',)
