from flask import Blueprint

music = Blueprint('music', __name__)

from . import views