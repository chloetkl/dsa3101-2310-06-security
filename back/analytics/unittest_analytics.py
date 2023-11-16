import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from nuseda import plots, convert_dataframe
from generate_heatmap import heatmap
from map_pin import generate_map_points
import os

class TestPlotsFunction(unittest.TestCase):

    @patch('nuseda.establish_sql_connection')
    def test_plots(self, mock_establish_sql_connection):
        # Mock SQL connection and cursor
        mock_establish_sql_connection.return_value = (MagicMock(), MagicMock())

        # Call the plots function
        result = plots()

        # Assert that the function returns the expected message
        expected_result = "HTMLs generated"
        self.assertEqual(result, expected_result)

        # Check if the HTML files were generated
        html_files = ['Monthly_Counts_by_Year.html', 'Daily_Counts_by_Year.html', 'Hourly_Counts_by_Year.html', 'Count_of_Location_by_Year.html', 'Count_of_Incidents_by_Year.html']

        for html_file in html_files:
            self.assertTrue(os.path.isfile(f'static/{html_file}'), f"HTML file '{html_file}' not found.")

        # Assert that the SQL connection and cursor were called
        mock_establish_sql_connection.assert_called_once()

        # Assert that the fetchall method was called
        mock_establish_sql_connection.return_value[1].fetchall.assert_called_once()

    @patch('generate_heatmap.establish_sql_connection')
    def test_heatmap(self, mock_establish_sql_connection):
        # Mock SQL connection and cursor
        mock_establish_sql_connection.return_value = (MagicMock(), MagicMock())

        # Mock the result of the SQL query
        mock_establish_sql_connection.return_value[1].fetchall.return_value = [
            {'Latitude': 1.35, 'Longitude': 103.82},
            {'Latitude': 1.36, 'Longitude': 103.83},
            # Add more data as needed
        ]

        # Call the heatmap function
        result = heatmap()

        # Assert that the function returns the expected message
        expected_result = "Heatmap generated."
        self.assertEqual(result, expected_result)

        # Check if the HTML file was generated
        self.assertTrue(os.path.isfile('static/heatmap.html'), "Heatmap HTML file not found.")

        # Assert that the SQL connection and cursor were called
        mock_establish_sql_connection.assert_called_once()

        # Assert that the fetchall method was called
        mock_establish_sql_connection.return_value[1].fetchall.assert_called_once()
    
    @patch('map_pin.establish_sql_connection')
    def test_generate_map_points(self,  mock_establish_sql_connection):
        # Mock SQL connection and cursor
        mock_establish_sql_connection.return_value = (MagicMock(), MagicMock())

        # Mock SQL query result
        mock_establish_sql_connection.return_value[1].fetchall.return_value = [
            (1.35, 103.82, 'Incident 1', 'High'),
            (1.36, 103.83, 'Incident 2', 'Normal')
            # Add more rows as needed
        ]

        # Call the function to generate the map
        result = generate_map_points()

        # Assertions
        self.assertEqual(result, "Map generated.")

        # Verify that SQL connection and cursor were called
        mock_establish_sql_connection.assert_called_once()

        # Assert that the fetchall method was called
        mock_establish_sql_connection.return_value[1].fetchall.assert_called_once()
    
    def setUp(self):
        # Sample data for testing
        self.sample_data = {
            'Time': ['2023-01-01 08:30:00', '2023-02-15 15:45:00', '2023-03-20 21:00:00','2023-03-20 02:00:00','2023-03-20 13:00:00','2023-03-20 07:00:00'],
            # Add other columns as needed
        }

    def test_convert_dataframe(self):
        # Create a DataFrame from sample data
        df = pd.DataFrame(self.sample_data)

        # Call the function to convert the DataFrame
        df_result = convert_dataframe(df)

        # Assertions
        self.assertTrue('Year' in df_result.columns)
        self.assertTrue('DayOfYear' in df_result.columns)
        self.assertTrue('Month' in df_result.columns)
        self.assertTrue('DayOfWeek' in df_result.columns)
        self.assertTrue('HourOfDay' in df_result.columns)

        # Check if the 'HourOfDay' column has been mapped correctly
        expected_hour_categories = set([
            'Late Night', 'Early Morning', 'Morning', 'Afternoon',
            'Evening', 'Night'
        ])
        self.assertEqual(set(df_result['HourOfDay'].unique()), expected_hour_categories)

if __name__ == '__main__':
    unittest.main()
