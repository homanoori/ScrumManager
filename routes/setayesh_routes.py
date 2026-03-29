from flask import Blueprint, render_template, redirect, request
from database import get_connection

setayesh_bp = Blueprint("setayesh", __name__)

# Setayesh adds her routes here