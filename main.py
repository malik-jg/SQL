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

    # Allows prospective users to create an account in the system
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Gets new registration formation, checks, then generates the new account information in the databasereg
    isitration"""

    if request.method == "POST":
        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        dob_str = request.form.get("dob")
        email = request.form.get("email")
        username = request.form.get("username").capitalize()
        password = request.form.get("password")
        street_address = request.form.get("street_address")
        city = request.form.get("city")
        state = request.form.get("state")
        postal_code = request.form.get("postal_code")

        if not all([first_name, last_name, dob_str, email, username, password, street_address, city, state, postal_code]):
            flash("Please fill in all required fields!", "Failed")
            return render_template("signup.html")

        if check_email(email, connect_db()) is not None:

            flash("Email already exists!", "Failed")

            return render_template("signup.html")
        else:

            new_user = add_user(first_name, last_name, dob_str, email, username, password, street_address, city, state, postal_code, connect_db())

            if new_user:
                flash("Signup successful! Please login.", "Success")
                return render_template("login.html")
            else:
                flash("Signup failed. Please try again.", "Faied")
                return render_template("signup.html")

    return render_template("signup.html")


# Brings a user to their homepage depending on their role
@app.route("/home", methods=["GET", "POST"])
def home():
    """Brings the user the the correct home page based on
    the role saved within the session variable"""
    if "role" not in session:
        return render_template("login.html")

    role = session["role"]
    if role == "admin":
        return render_template("adminhome.html")
    elif role == "reviewer":
        return render_template("reviewhome.html")
    elif role == "instructor":
        return render_template("instructor_dashboard.html")
    elif role == "grad_stu":
        return render_template("student_dashboard.html")
    elif role == "alummi":
        return render_template("alumni_dashboard.html")
    elif role == "fac_adv":
        return render_template("advisor_dashboard.html")
    else:
        return render_template("applicanthome.html")
# Form One for Registration
@app.route("/form_one", methods = ['GET','POST'])
def form_one():
    message = None
    user_id = session['user_id']
    program = get_student_information(get_university_id(user_id, connect_db())['uid'], connect_db())['program']
    course_catalog = (get_course_catalog(connect_db()))
    required_courses = get_required_courses(program, connect_db())
    requirements = get_requirements(program, connect_db())
    if request.method == 'POST':
        form_one = []
        for course in course_catalog:
            course_name = "select_" + str(course['department']) + "" + str(course['course_num'])
            course_form_name = request.form.get(course_name)
            if course_form_name:
                form_one.append(course)
        if not form_one:
            message = f"Please do not submit an empty form!"
            return render_template("form_one.html", course_catalog = course_catalog, program = program, message = message, required_courses=required_courses, requirements=requirements)
        validation = check_form_one(form_one, program, connect_db())
        if not validation == 'valid':
            message = validation
            return render_template("form_one.html", course_catalog = course_catalog, program = program, message = message, required_courses=required_courses, requirements=requirements)
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO forms (submitted_university_id) VALUES (%s)", (get_university_id(user_id, connect_db())['uid'],))
        db.commit()
        cursor.execute("SELECT form_id FROM forms WHERE forms.submitted_university_id = (%s) ORDER BY form_id DESC LIMIT 1", (get_university_id(user_id, connect_db())['uid'],))
        form_id = cursor.fetchone()[0]
        for course in form_one:
            cursor.execute("INSERT INTO forms_classes (form_id, university_id, dept, course_num, credits) VALUES (%s, %s, %s, %s, %s)", (form_id, get_university_id(user_id, connect_db())['uid'], course['department'], course['course_num'], course['credit']))
            db.commit()
        if program == 'PhD':
            thesis = request.form['large-text']
            cursor.execute("INSERT INTO thesis (form_id, thesis, submitted_university_id) VALUES (%s, %s, %s)", (form_id, thesis, get_university_id(user_id, connect_db())['uid']))
            db.commit()
        message = f"You have successfully submitted your form 1!"
    return render_template("form_one.html", course_catalog = course_catalog, program = program, message = message, required_courses=required_courses, requirements=requirements)
# Register for Classes
@app.route("/register_for_classes", methods=['GET','POST'])
def register_for_classes():
    message = None
    uid = get_university_id(session['user_id'], connect_db())['uid']
    student_information = get_student_information(uid, connect_db())
    if student_information['advising_hold'] == 0:
        return redirect(url_for("student_dashboard", message = "You have an advising hold!"))
    course_schedule = get_course_schedule(connect_db())
    course_catalog = (get_course_catalog(connect_db()))
    form_classes = get_form_classes(uid, connect_db())
    search_query = request.args.get('search')
    if search_query:
       course_schedule = get_filtered_course_schedule(search_query, connect_db())
    if request.method == 'POST':
        if request.form.get('filter_check'):
            filtered_array = request.args.get("filteredArray")
            print(filtered_array)
        else:
            course_schedule_registration = []
            for course in course_schedule:
                course_name = "select_" + str(course['course_dept']) + "" + str(course['course_num']) + "" + str(course['crn'])
                course_registration_name = request.form.get(course_name)
                if course_registration_name:
                    course_schedule_registration.append(course)
            if not course_schedule_registration:
                message = f"Please do not submit an empty registration!"
                return render_template("register_for_classes.html", course_schedule = course_schedule, course_catalog = course_catalog, message = message, form_classes=form_classes)
            # if not overlap_check(course_schedule_registration):
            #     message = "You have overlapping classes"
            #     return render_template("register_for_classes.html", course_schedule = course_schedule, course_catalog = course_catalog, message = message, form_classes=form_classes)
            if student_information['program'] == 'PhD':
                if not phd_registration_check(course_schedule_registration):
                    message = 'You can only register for 6000s classes'
                    return render_template("register_for_classes.html", course_schedule = course_schedule, course_catalog = course_catalog, message = message, form_classes=form_classes)
            db = connect_db()
            cursor = db.cursor()
            for course in course_schedule_registration:
                course_info = course_reg_to_course(course['course_dept'],course['course_num'], connect_db())
                cursor.execute("INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, year, crn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (uid, course_info['department'], course_info['course_num'], course_info['title'], course_info['credit'], course['semester'], course['year'], course['crn']))
                db.commit()
            message = f"You have successfully registered for classes!"
    return render_template("register_for_classes.html", course_schedule = course_schedule, course_catalog = course_catalog, message = message, form_classes=form_classes)
# Student Dashboard
@app.route("/student_dashboard", methods=['GET','POST'])
def student_dashboard():
    message = None
    thesis = None
    if request.args.get('message'):
       message = request.args.get('message')

    uid = get_university_id(session['user_id'], connect_db())['uid']

    student_information = get_student_information(uid, connect_db())

    courses_taken = get_courses_taken(uid, connect_db())
    form_one = get_form_one(uid, connect_db())
    form_classes = get_form_classes(uid, connect_db())

    if student_information['program'] == 'PhD':
        thesis = get_thesis(uid, connect_db())

    graduation_application = get_graduation_application(uid, connect_db())
        
    if request.method == 'POST':
        if request.form.get('Process'):
            drop_courses = []
            for course in courses_taken:
                course_name = "select_" + str(course['dept']) + "" + str(course['course_num']) + "" + str(course['crn'])
                drop = request.form.get(course_name)
                if drop:
                    drop_courses.append(course)
            db = connect_db()
            cursor = db.cursor()
            for course in drop_courses:
                cursor.execute("DELETE FROM course_taken WHERE course_taken.dept = %s AND course_taken.course_num = %s AND course_taken.crn = %s AND university_id = %s", (course['dept'], course['course_num'], course['crn'], uid))
                db.commit()
            message = f"You have dropped the selected courses!"
            return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)
        if request.form.get('graduation'):
            if not form_one:
                message = "You have not submitted a Form 1!"
                return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)
            if not form_one['approved']:
                message = "Your Form 1 is not approved!"
                return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)
            if not courses_taken:
                message = "You have not taken any courses!"
                return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)
            audit = graduation_application_audit(student_information, courses_taken, connect_db())
            if not audit == "Pass":
                message = audit
            else:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("INSERT INTO graduation_application (submitted_university_id) VALUES (%s)", (uid,))
                db.commit()
                message = "You have successfully submitted your graduation application!"
        if request.form.get('to_alumni'):
            print("ALUMNI")
            to_alumni(uid, connect_db())
    return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)


@app.route("/view_classes", methods=['GET','POST'])
def view_classes():
    user_id = session['user_id']
    
    assigned_classes = get_assigned_classes(user_id, connect_db())
