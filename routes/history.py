from flask import Blueprint, render_template, request

from db import get_db
from services import history as svc

bp = Blueprint("history", __name__, url_prefix="/history")


@bp.get("")
def list_history():
    q, error = svc.clean_query(request.args.get("q"))
    rows = [] if error else svc.completed(get_db(), q)
    return render_template("history/list.html", rows=rows, q=q, error=error), (400 if error else 200)