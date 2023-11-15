from functools import wraps
from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
import pandas as pd

from connect_sql import establish_sql_connection
from back.database.users.users import add_user

admin_bp = Blueprint('admin', __name__)

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated and current_user.role == required_role:
                return func(*args, **kwargs)
            else:
                return f"Unauthorized, page only accessible to {required_role}", 403  # Adjust the response accordingly
        return wrapper
    return decorator

# Define endpoints within the Blueprint
@admin_bp.route('/admin', methods=['GET'])
@login_required
@role_required('admin')
def admin():
    try:
        db,cursor = establish_sql_connection()
        query = f"SELECT Users.id as 'User ID', Users.username as 'Username', \
            Users.email as 'Email', User_roles.role as 'Role'\
            FROM Users LEFT JOIN User_roles ON Users.role_id = User_roles.id;"
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        data = pd.DataFrame(result, columns = columns)

        data = data[['User ID', 'Username', 'Email', 'Role']]
        data_dict = data.to_dict(orient='records')
        return render_template('admin.html', data=data_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Define endpoints within the Blueprint
@admin_bp.route('/admin/add-new-user', methods=['POST'])
@login_required
@role_required('admin')
def add_new_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        email = data.get('email',None)
        add_user(username,password,role,email)
        return jsonify({'message': 'User added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
