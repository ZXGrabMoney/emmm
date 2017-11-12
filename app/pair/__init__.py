from flask import Blueprint

pair = Blueprint('pair', __name__)

from . import views