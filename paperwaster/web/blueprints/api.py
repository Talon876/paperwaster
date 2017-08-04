from flask import Blueprint, request, render_template

from paperwaster.web.app import db

api = Blueprint('api', __name__)
