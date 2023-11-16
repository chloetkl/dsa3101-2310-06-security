from functools import wraps
from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from back.database.users.users import authenticate
from connect_sql import establish_sql_connection
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.secret_key = 'secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

## Add Blueprints
from app.admin import admin_bp
app.register_blueprint(admin_bp)
from app.security import security_bp
app.register_blueprint(security_bp)
from app.analytics import analytics_bp
app.register_blueprint(analytics_bp)


## For Authentication
class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

def get_user_from_username(username):
    db,cursor = establish_sql_connection()
    query = f'SELECT Users.id, Users.username, User_roles.role \
        FROM Users LEFT JOIN User_roles ON Users.role_id = User_roles.id \
            WHERE Users.username = "{username}";'

    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()

    # Check if the result is not None
    if result:
        user_id, username, role = result
        print(f'User {username} added')
        return User(user_id, username,role)
    else:
        print('No user found')
        return None

@login_manager.user_loader
def load_user(user_id):
    db,cursor = establish_sql_connection()
    query = f'SELECT Users.id, Users.username, User_roles.role \
        FROM Users LEFT JOIN User_roles ON Users.role_id = User_roles.id \
            WHERE Users.id= "{user_id}";'

    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()

    # Check if the result is not None
    if result:
        user_id, username, role = result
        print(f'User {username} logged in')
        return User(user_id, username,role)
    else:
        print('No user found')
        return None


def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated and current_user.role == required_role:
                return func(*args, **kwargs)
            else:
                return "Unauthorized", 403  # Adjust the response accordingly
        return wrapper
    return decorator

## Home - Login page
@app.route('/', methods=['GET'])
def home():
    try:
        return render_template('home.html'), 200
    except Exception as e:
        error_message = f"Error rendering template: {e}"
        return jsonify({'error': error_message}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['UserID']
        password = request.form['Password']

        authenticated, role = authenticate(username,password)

        if authenticated:
            user = get_user_from_username(username) # create user
            login_user(user)
        else:
            return "Invalid UserID or Password", 401

        if role == 'security':
            return redirect(url_for('security.security')), 302
        elif role == 'analytics':
            return redirect(url_for('analytics.analytics')), 302
        elif role == 'admin':
            return redirect(url_for('admin.admin')), 302
    except HTTPException as http_error:
        return jsonify({'error': str(http_error)}), http_error.code
    except Exception as e:
        return jsonify({'error': f"Internal Server Error: {e}"}), 500




@app.route('/logout', methods=['GET'])
def logout():
    try:
        logout_user()
        return redirect('/'), 302
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
