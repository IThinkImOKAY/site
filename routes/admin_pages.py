from __main__ import app
from flask import render_template
from helpers.wrappers import *

@app.get("/*/admin/")
@auth_required
@admin_required
def admin_index(u):

    return render_template("admin/index.html", u = u)

@app.get("/*/admin/defaults")
@auth_required
@admin_required
def admin_defaults(u):

    return render_template("admin/defaults.html", u = u)
