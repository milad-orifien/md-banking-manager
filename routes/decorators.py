from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(view_function):
    @wraps(view_function)
    def wrapped(*args, **kwargs):
        if not session.get("kundenid"):
            flash("Bitte zuerst anmelden.", "warning")
            return redirect(url_for("auth.login"))
        return view_function(*args, **kwargs)

    return wrapped
