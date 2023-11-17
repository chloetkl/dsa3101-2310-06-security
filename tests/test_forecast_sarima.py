import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
import back.models.sarima.sarima_model as sarima_model

class TestForecastSarima(unittest.TestCase):

    @patch('back.models.sarima.sarima_model.pickle.load')
    @patch('back.models.sarima.sarima_model.open', new_callable=unittest.mock.mock_open, read_data='model data')
    @patch('back.models.sarima.sarima_model.go.Figure')
    def test_forecast_sarima(self, mock_figure, mock_open, mock_pickle_load):
        # Mock the SARIMA model
        mock_model = MagicMock()
        mock_model.predict.return_value = [10] * 52  # Dummy forecast data
        mock_pickle_load.return_value = mock_model

        # Mock the plotly figure
        mock_fig_instance = MagicMock()
        mock_figure.return_value = mock_fig_instance

        # Call the function with a test incident type
        incident_type = 'LOST AND FOUND'
        result = sarima_model.forecast_sarima(incident_type)

        # Assertions
        mock_open.assert_called_once_with(f'back/models/sarima/sarima_model_{incident_type}.pkl', 'rb')
        mock_model.predict.assert_called_once_with(n_periods=52)

if __name__ == '__main__':
    unittest.main()
