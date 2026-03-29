from flask import Blueprint, render_template
from database import get_connection

sasan_bp = Blueprint("sasan", __name__)

# Sasan adds his routes here