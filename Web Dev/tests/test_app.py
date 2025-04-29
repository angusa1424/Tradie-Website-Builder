import unittest
from backend.app import app
import json

class Test3ClickBuilder(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_create_website(self):
        test_data = {
            'businessName': 'Test Business',
            'serviceType': 'Consulting',
            'location': 'New York'
        }
        response = self.app.post('/api/create-website',
                               data=json.dumps(test_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('url', data)

    def test_generate_website(self):
        test_data = {
            'businessName': 'Test Business',
            'serviceType': 'Consulting',
            'location': 'New York'
        }
        response = self.app.post('/generate',
                               data=json.dumps(test_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('html', data)

    def test_download_pdf(self):
        test_data = {
            'businessName': 'Test Business',
            'serviceType': 'Consulting',
            'location': 'New York'
        }
        response = self.app.post('/download-pdf',
                               data=json.dumps(test_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')

    def test_publish_website(self):
        test_data = {
            'businessName': 'Test Business',
            'serviceType': 'Consulting',
            'location': 'New York'
        }
        response = self.app.post('/publish',
                               data=json.dumps(test_data),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('url', data)

if __name__ == '__main__':
    unittest.main() 