from flask import Blueprint, render_template

blueprint = Blueprint('subMarks', __name__, template_folder='templates', static_folder='static')

LABEL = 'subMarks'
ADMIN_LABEL = 'subMarks Admin'

import subMarks.core

def get_admin_panel():
    return render_template('widgets/admin_panel.html')