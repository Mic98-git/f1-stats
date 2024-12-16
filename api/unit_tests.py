import unittest
import json
from main import app

class F1StatsTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_circuit_summary_valid(self):
        # Test without any filters
        response = self.app.get('/circuit-summary')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)  # Check if the response is a list
        self.assertGreater(len(data), 0)  # Ensure there is at least one circuit in the response

        # Test with a valid circuit name filter
        response = self.app.get('/circuit-summary?name=Albert')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)  # Ensure there is at least one circuit matching the filter

    def test_circuit_summary_invalid(self):
        # Test with an invalid circuit name filter
        response = self.app.get('/circuit-summary?name=NonExistentCircuit')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No circuit found with the given name')

    def test_driver_summary_valid(self):
        # Test without any filters
        response = self.app.get('/driver-summary')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)  # Check if the response is a list
        self.assertGreater(len(data), 0)  # Ensure there is at least one driver in the response

        # Test with a valid driver code filter
        response = self.app.get('/driver-summary?code=HAM')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)  # Ensure there is at least one driver matching the filter

        # Test with a valid driver ID filter
        response = self.app.get('/driver-summary?id=1')  # Assuming driver ID 1 exists
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)  # Ensure there is at least one driver matching the ID

    def test_driver_summary_invalid(self):
        # Test with an invalid driver code filter
        response = self.app.get('/driver-summary?code=NonExistentCode')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No driver found with the given code')

        # Test with an invalid driver ID filter
        response = self.app.get('/driver-summary?id=9999')  # Assuming driver ID 9999 does not exist
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'No driver found with the given ID')

if __name__ == '__main__':
    unittest.main()