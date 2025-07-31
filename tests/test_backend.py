# tests/test_backend.py

import unittest
import pandas as pd
import tempfile
import os
import json
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the app directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
app_dir = os.path.join(project_root, 'app')
sys.path.insert(0, app_dir)

# Now import from backend
from backend import (
    SecurityConfig, RateLimiter, DataCache,
    carregar_json, salvar_json, atualizar_contexto_pagador,
    processar_extrato_credito, processar_extrato_debito,
    aplicar_regras_contexto, criar_graficos
)

class TestSecurityConfig(unittest.TestCase):
    """Test security configuration functions."""
    
    def test_validate_api_key_valid(self):
        """Test valid API key validation."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test123'}):
            self.assertTrue(SecurityConfig.validate_api_key())
    
    def test_validate_api_key_invalid(self):
        """Test invalid API key validation."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid-key'}):
            self.assertFalse(SecurityConfig.validate_api_key())
    
    def test_validate_api_key_missing(self):
        """Test missing API key validation."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(SecurityConfig.validate_api_key())
    
    def test_validate_file_path_safe(self):
        """Test safe file path validation."""
        self.assertTrue(SecurityConfig.validate_file_path("data/test.csv"))
    
    def test_validate_file_path_unsafe(self):
        """Test unsafe file path validation."""
        self.assertFalse(SecurityConfig.validate_file_path("../../../etc/passwd"))
    
    def test_validate_input_length_valid(self):
        """Test valid input length."""
        self.assertTrue(SecurityConfig.validate_input_length("Hello"))
    
    def test_validate_input_length_too_long(self):
        """Test input length too long."""
        long_input = "x" * 2000
        self.assertFalse(SecurityConfig.validate_input_length(long_input))

class TestRateLimiter(unittest.TestCase):
    """Test rate limiter functionality."""
    
    def setUp(self):
        """Set up test rate limiter."""
        self.rate_limiter = RateLimiter(max_calls=2, time_window=60)
    
    def test_can_call_initial(self):
        """Test initial call allowed."""
        self.assertTrue(self.rate_limiter.can_call())
    
    def test_can_call_limit_reached(self):
        """Test call limit reached."""
        self.rate_limiter.can_call()
        self.rate_limiter.can_call()
        self.assertFalse(self.rate_limiter.can_call())
    
    def test_can_call_reset_after_window(self):
        """Test calls reset after time window."""
        self.rate_limiter.can_call()
        self.rate_limiter.can_call()
        
        # Mock time to advance beyond window
        with patch('time.time') as mock_time:
            mock_time.return_value = 100  # Advance time
            self.assertTrue(self.rate_limiter.can_call())

class TestDataCache(unittest.TestCase):
    """Test data caching functionality."""
    
    def setUp(self):
        """Set up test cache."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = DataCache(self.temp_dir)
    
    def tearDown(self):
        """Clean up test cache."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_set_and_get(self):
        """Test setting and getting cache data."""
        test_data = {"test": "data"}
        self.cache.set("test_key", test_data)
        retrieved_data = self.cache.get("test_key")
        self.assertEqual(retrieved_data, test_data)
    
    def test_get_nonexistent(self):
        """Test getting nonexistent cache data."""
        self.assertIsNone(self.cache.get("nonexistent_key"))

class TestJSONFunctions(unittest.TestCase):
    """Test JSON utility functions."""
    
    def setUp(self):
        """Set up test file."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test file."""
        os.unlink(self.temp_file.name)
    
    def test_carregar_json_existing(self):
        """Test loading existing JSON file."""
        test_data = {"key": "value"}
        with open(self.temp_file.name, 'w') as f:
            json.dump(test_data, f)
        
        loaded_data = carregar_json(self.temp_file.name)
        self.assertEqual(loaded_data, test_data)
    
    def test_carregar_json_nonexistent(self):
        """Test loading nonexistent JSON file."""
        loaded_data = carregar_json("nonexistent.json")
        self.assertEqual(loaded_data, {})
    
    def test_salvar_json(self):
        """Test saving JSON data."""
        test_data = {"key": "value"}
        salvar_json(self.temp_file.name, test_data)
        
        with open(self.temp_file.name, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_data)

class TestDataProcessing(unittest.TestCase):
    """Test data processing functions."""
    
    def setUp(self):
        """Set up test data."""
        self.test_df = pd.DataFrame({
            'Data': ['01/01/2025', '02/01/2025'],
            'Estabelecimento': ['Test Store 1', 'Test Store 2'],
            'Valor': ['100,00', '200,00'],
            'Tipo': ['Despesa', 'Despesa']
        })
    
    def test_aplicar_regras_contexto(self):
        """Test applying context rules to DataFrame."""
        contexto = {
            "Test Store 1": {"categoria": "Alimentação", "pagador": "Arthur"},
            "Test Store 2": {"categoria": "Transporte", "pagador": "Pai"}
        }
        
        result_df = aplicar_regras_contexto(self.test_df, contexto)
        
        self.assertIn('Categoria', result_df.columns)
        self.assertIn('Pagador', result_df.columns)
        self.assertEqual(result_df.iloc[0]['Categoria'], 'Alimentação')
        self.assertEqual(result_df.iloc[0]['Pagador'], 'Arthur')
    
    def test_criar_graficos_empty(self):
        """Test creating graphs with empty DataFrame."""
        empty_df = pd.DataFrame()
        fig_col, fig_line = criar_graficos(empty_df)
        
        # Should return empty figures
        self.assertIsInstance(fig_col, object)
        self.assertIsInstance(fig_line, object)

class TestCSVProcessing(unittest.TestCase):
    """Test CSV processing functions."""
    
    def setUp(self):
        """Set up test CSV file."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        self.temp_file.write("Data movimento;Nome do fornecedor/cliente;Valor (R$)\n")
        self.temp_file.write("01/01/2025;Test Store;100,00\n")
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test file."""
        os.unlink(self.temp_file.name)
    
    def test_processar_extrato_credito(self):
        """Test processing credit card statement."""
        result_df = processar_extrato_credito(self.temp_file.name)
        
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIn('Data', result_df.columns)
        self.assertIn('Estabelecimento', result_df.columns)
        self.assertIn('Valor', result_df.columns)
        self.assertIn('Tipo', result_df.columns)
        
        # Check that values are negative (expenses)
        self.assertTrue(all(result_df['Valor'] < 0))
    
    def test_processar_extrato_credito_invalid_path(self):
        """Test processing with invalid file path."""
        with self.assertRaises(ValueError):
            processar_extrato_credito("../../../etc/passwd")

if __name__ == '__main__':
    unittest.main() 