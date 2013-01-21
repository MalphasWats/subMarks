from flask import Blueprint, render_template

blueprint = Blueprint('subMarks', __name__, template_folder='templates', static_folder='static')

LABEL = 'subMarks'
ADMIN_LABEL = 'subMarks Admin'
ICON = 'bookmark-empty'

import subMarks.core

from subMarks.core import get_admin_panel