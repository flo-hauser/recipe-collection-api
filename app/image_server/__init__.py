"""
serve static images for development
"""

from flask import Blueprint

bp = Blueprint("image_server", __name__)

from . import images
