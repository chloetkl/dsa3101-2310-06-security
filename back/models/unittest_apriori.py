import unittest
from unittest.mock import patch, MagicMock
from apriori import get_rank

class TestGetRankFunction(unittest.TestCase):

    @patch('apriori.establish_sql_connection')
    def test_get_rank_success(self, mock_establish_sql_connection):
        # Mock SQL connection and cursor
        mock_establish_sql_connection.return_value = (MagicMock(), MagicMock())
        
        # Mock the result of the SQL query
        mock_establish_sql_connection.return_value[1].fetchall.return_value = [('PGP', '2023-11-11 14:00:00'),('TIH', '2023-11-11 12:00:00')]

        # Test the get_rank function
        result = get_rank(location='PGP', day='Saturday', hour='Afternoon')

        # Assert the expected result
        expected_result = "['Afternoon', 'PGP', 'Saturday'] : Priority 1 out of 2"
        self.assertEqual(result, expected_result)

    @patch('apriori.establish_sql_connection')
    def test_get_rank_error(self, mock_establish_sql_connection):
        # Mock SQL connection and cursor
        mock_establish_sql_connection.return_value = (MagicMock(), MagicMock())
        
        # Mock the result of the SQL query
        mock_establish_sql_connection.return_value[1].fetchall.return_value = []

        # Test the get_rank function with an error condition
        result = get_rank(location='NonExistentLocation', day='Sunday', hour='Evening')

        # Assert the expected error message
        expected_result = "['Evening', 'NonExistentLocation', 'Sunday'] Error: Check spelling or format! e.g. location=PGP, day=Saturday, hour=Afternoon \nOR \nNew Combination. Please add to the database!"
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
