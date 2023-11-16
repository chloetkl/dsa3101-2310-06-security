import subprocess

#Uncomment to install required packages if needed
#subprocess.run(["pip", "install", "-r", "requirements.txt"])

import unittest
from flask import Flask, url_for
from flask_login import LoginManager, login_user
from flask_testing import TestCase
from unittest.mock import patch, MagicMock
from nusecure import load_user
from connect_sql import establish_sql_connection, get_location_id, get_incident_type_id

from app.security import security_bp

class TestSecurityEndpoints(TestCase):

    def create_app(self):
        # Create a new Flask app for testing
        test_app = Flask(__name__)
        test_app.config['TESTING'] = True
        test_app.secret_key = 'secret_key'
        test_app.register_blueprint(security_bp)
        
        # Initialize LoginManager
        login_manager = LoginManager()
        login_manager.init_app(test_app)

        @login_manager.user_loader
        def load_user_callback(user_id):
            return load_user(user_id)

        # Register blueprints, add routes, etc. (if needed)

        with test_app.app_context():
            # Anything you want to do within the app context during testing
            pass

        return test_app
    
    def setUp(self):
        self.app = self.create_app()
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

        #@self.app.login_manager.user_loader
        #def load_user(user_id):
            #return load_user(user_id)
        # ... other setup code .

    def tearDown(self):
        self.app_context.pop()
    
    @patch('connect_sql.establish_sql_connection')
    @patch('mysql.connector.connect')
    #@patch('nusecure.establish_sql_connection')
    def test_security_page(self, mock_mysql_connect, mock_establish_sql_connection):
        # Mock SQL connection and cursor
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_establish_sql_connection.return_value = (mock_db, mock_cursor)
        mock_cursor.fetchone.return_value = (2, 'sec1', 'security')
        mock_mysql_connect.return_value = MagicMock()


        user = load_user(2)
        login_user(user)

        response = self.client.get(url_for('security.security'))
        self.assert200(response)
        # Add more assertions as needed

    @patch('connect_sql.establish_sql_connection')
    @patch('mysql.connector.connect')
    #@patch('nusecure.establish_sql_connection')
    def test_update_incident(self, mock_mysql_connect, mock_establish_sql_connection):
        # Mock SQL connection and cursor
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_establish_sql_connection.return_value = (mock_db, mock_cursor)
        mock_cursor.fetchone.return_value = (2, 'sec1', 'security')
        mock_mysql_connect.return_value = MagicMock()

        user = load_user(2)
        login_user(user)

        # Assuming you have a form with incident_id, status, and priority fields
        data = {'incident_id': '7911', 'status': 'Open', 'priority': 'Normal'}

        response = self.client.post(url_for('security.update_incident', _external = True), data=data)
        self.assertRedirects(response, url_for('security.security'))
        # Add more assertions as needed

    @patch('connect_sql.generate_map_points')
    @patch('mysql.connector.connect')
    def test_map_pin_generation(self, mock_generate_map_points, mock_establish_sql_connection):
        mock_establish_sql_connection.return_value = (MagicMock(), MagicMock())

        user = load_user(2)
        login_user(user)

        mock_generate_map_points.return_value = 'mocked_map_points_response'

        response = self.client.get(url_for('security.map_pin_generation'))
        self.assert200(response)
        self.assertEqual(response.get_data(as_text=True), 'mocked_map_points_response')
        # Add more assertions as needed

    @patch('connect_sql.establish_sql_connection')
    @patch('mysql.connector.connect')
    #@patch('nusecure.establish_sql_connection')
    def test_add_incident_report(self, mock_mysql_connect, mock_establish_sql_connection):
        # Mock SQL connection and cursor
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_establish_sql_connection.return_value = (mock_db, mock_cursor)
        mock_cursor.fetchone.return_value = (2, 'sec1', 'security')
        mock_mysql_connect.return_value = MagicMock()

        user = load_user(2)
        login_user(user)

        # Assuming you have a form with description, type, datetime, priority, location, and status fields
        data = {
            'description': 'Test',
            'type': 'LOST AND FOUND',
            'datetime': '2023-11-16 12:00:00',
            'priority': 'Normal',
            'building': 'SRC MINI GRAND STAND',
            'status': 'Open'
        }

        response = self.client.post(url_for('security.add_incident_report'), data=data)
        self.assert200(response)
        # Add more assertions as needed

if __name__ == '__main__':
    unittest.main()