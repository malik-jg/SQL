import mysql.connector
import mysql.connector.cursor

sender_email = "amzgwu@gmail.com"
password = "yosj bbse rxzq pfna"
imap_server = "imap.gmail.com"

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/static/transcript'

def clear_session(session) -> None:
    """Clears all session variables"""

    if "username" in session:
        session.pop("username")
    if "email" in session:
        session.pop("email")
    if "role" in session:
        session.pop("role")
    if "question_history" in session:
        session.pop("question_history")
    if "response_history" in session:
        session.pop("response_history")

    session.clear()

    return

def check_login(
    email: str, password: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """checks the login, then returns all data related to the user
    (user_id, Email, Username, Password, Role)"""

    cursor = db.cursor(dictionary=True)

    checklogin = "SELECT * FROM user WHERE email = %s AND password = %s"
    checkloginvalues = (email, password)

    cursor.execute(checklogin, checkloginvalues)

    userdata = cursor.fetchone()
    if userdata is not None:
        cursor.close()
        return userdata

    return None