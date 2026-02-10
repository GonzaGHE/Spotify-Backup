import unittest
from unittest.mock import MagicMock, patch
from src.client import SpotifyClient

class TestSpotifyClient(unittest.TestCase):
    def setUp(self):
        self.client = SpotifyClient("fake_token")

    @patch('src.client.requests.get')
    def test_conectar_success(self, mock_get):
        # Mock de respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'user123', 'display_name': 'Test User'}
        mock_get.return_value = mock_response

        result = self.client.conectar()
        
        self.assertTrue(result)
        self.assertEqual(self.client.user_id, 'user123')
        self.assertEqual(self.client.display_name, 'Test User')

    @patch('src.client.requests.get')
    def test_conectar_failure(self, mock_get):
        # Mock de respuesta fallida
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = self.client.conectar()
        
        self.assertFalse(result)

    @patch('src.client.requests.get')
    def test_get_playlists(self, mock_get):
        # Mock de paginación
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 200
        mock_resp1.json.return_value = {
            'items': [
                {'name': 'PL1', 'owner': {'id': 'user123'}, 'public': True, 'description': 'desc', 'tracks': {'href': 'url'}, 'uri': 'uri1'},
                {'name': 'PL2', 'owner': {'id': 'other'}, 'public': True, 'description': 'desc', 'tracks': {'href': 'url'}, 'uri': 'uri2'} # De otro
            ],
            'next': None
        }
        mock_get.return_value = mock_resp1
        
        self.client.user_id = 'user123' # Simulamos que ya conectó
        playlists = self.client.get_playlists()

        self.assertEqual(len(playlists), 1) # Solo PL1 debería estar
        self.assertEqual(playlists[0]['name'], 'PL1')

if __name__ == '__main__':
    unittest.main()
