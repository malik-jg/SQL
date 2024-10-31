from flask import Flask, flash, session, render_template, redirect, url_for, request, jsonify
from flask import Flask, flash, request, redirect, url_for
from database import (
    connect_db
)
from functions import (
    check_login,
    clear_session,
)

app = Flask("app")
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = '/static/transcript'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Page On Load, Login Page : from here one can login or register for a new account
@app.route("/", methods=["GET", "POST"])
def login():
    """Routes you based on signup or login, if signup go to the signup template, if login, the session variables are initialized and routed to the roles homepage"""
    if request.method == "POST":

        if "Signup" in request.form:

            return render_template("signup.html")

        if "Login" in request.form:

            email = request.form.get("Email")
            password = request.form.get("Password")

            if not all([email, password]):
                flash("Please fill in all required fields!", "Failed")
                return render_template("login.html")

            user = check_login(email, password, connect_db())

            if user is None:
                flash("Authencation Failed! ", "Failed")
                return render_template("login.html")

            # Initialize Session Variables

            if "user_id" not in session:
                session["user_id"] = user["user_id"]

            if "first_name" not in session:
                session["first_name"] = user["first_name"]

            if "last_name" not in session:
                session["last_name"] = user["last_name"]

            if "dob" not in session:
                session["dob"] = user["dob"]

            if "email" not in session:
                session["email"] = user["email"]

            if "username" not in session:
                session["username"] = user["username"]

            if "address" not in session:
                session["address"] = user["address"]

            if "role" not in session:
                session["role"] = user["role"]
            # Redirect to the right home based on the role

            return roleportal()

    clear_session(session)

    return render_template("login.html")

# For Everyone, Used to return to the original home page for a role
@app.route("/roleportal", methods=["GET", "POST"])
def roleportal():
    """Redirect to the proper home page depending on role"""

    user_id = session["user_id"]
    userrolerow = grab_role(user_id, connect_db())
    userrole = userrolerow["role"]

    if userrole == "applicant":

        return redirect(url_for("applicanthome"))

    if userrole == "admin":

        return redirect(url_for("adminhome"))

    if userrole == "reviewer":

        return redirect(url_for("reviewhome"))

    if userrole == "user":

        return redirect(url_for("userhome"))

    if userrole == "cac":

        return redirect(url_for("cachome"))

    if userrole == "grad_sec":

        return redirect(url_for("gschome"))
    
    if userrole == "grad_stu":

        return redirect(url_for("student_dashboard"))
    
    if userrole == "instructor":

        return redirect(url_for("instructor_dashboard"))
    if userrole == "alumni":
        return redirect(url_for("alumni_dashboard"))
    if userrole == "fac_adv":
        return redirect(url_for("advisor_dashboard"))
    if userrole == 'registrar':
        return redirect(url_for("reghome"))
