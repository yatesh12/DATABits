from flask import Blueprint
from controllers.dataset_controller import DatasetController

# This will be imported by app.py, so we'll create a simple blueprint
dataset_bp = Blueprint('dataset', __name__, url_prefix='/api')

# The actual routes will be registered in app.py since we need access to the storage objects
