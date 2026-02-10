import unittest
import os
import json
from src.utils import guardar_json, cargar_json

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_data.json"
        self.data = {"key": "value", "list": [1, 2, 3]}

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_guardar_y_cargar_json(self):
        # Probar guardar
        result = guardar_json(self.data, self.test_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_file))

        # Probar cargar
        loaded_data = cargar_json(self.test_file)
        self.assertEqual(loaded_data, self.data)

    def test_cargar_json_no_existente(self):
        result = cargar_json("archivo_fantasma.json")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
