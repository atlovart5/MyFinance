# finbot_project/app/config.py

import os
from typing import Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class AppConfig:
    """Centralized configuration for the FinBot application."""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    PROJECT_ROOT: Path = BASE_DIR.parent
    
    # Data directories
    PASTA_CREDITO: Path = PROJECT_ROOT / "data" / "raw" / "credito"
    PASTA_DEBITO: Path = PROJECT_ROOT / "data" / "raw" / "debito"
    PASTA_PROCESSADOS: Path = PROJECT_ROOT / "data" / "processed"
    PASTA_RELATORIOS: Path = PROJECT_ROOT / "data" / "relatorios"
    PASTA_FONTES: Path = PROJECT_ROOT / "fonts"
    PASTA_CACHE: Path = PASTA_PROCESSADOS / "cache"
    
    # Files
    ARQUIVO_CONTEXTO: Path = PASTA_PROCESSADOS / "contexto_financeiro.json"
    ARQUIVO_ORCAMENTO: Path = PASTA_PROCESSADOS / "orcamento.json"
    ARQUIVO_CONSOLIDADO: Path = PASTA_PROCESSADOS / "dados_consolidados.csv"
    
    # AI Configuration
    OPENAI_MODEL: str = "gpt-4.1-nano"  # Modelo padrão: GPT-4.1 Nano
    OPENAI_TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 4000
    
    # Available models for selection (GPT-4.1 Nano como primeiro)
    AVAILABLE_MODELS: List[str] = field(default_factory=lambda: [
        "gpt-4.1-nano",  # Modelo padrão - mais rápido e econômico
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-3.5-turbo"
    ])
    
    # Rate Limiting
    MAX_API_CALLS: int = 10
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    
    # Data Processing
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    SUPPORTED_ENCODINGS: List[str] = field(default_factory=lambda: ['utf-8', 'latin-1', 'cp1252'])
    SUPPORTED_SEPARATORS: List[str] = field(default_factory=lambda: [';', ',', '\t'])
    
    # UI Configuration
    PAGE_TITLE: str = "FinBot - Seu Assistente Financeiro"
    PAGE_ICON: str = "🤖"
    LAYOUT: str = "wide"
    
    # Security
    ALLOW_DANGEROUS_CODE: bool = True  # Permite execução de código Python no chatbot
    MAX_INPUT_LENGTH: int = 1000
    VALIDATE_FILE_PATHS: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Override with environment variables if present
        if os.getenv('OPENAI_MODEL'):
            config.OPENAI_MODEL = os.getenv('OPENAI_MODEL')
        
        if os.getenv('OPENAI_TEMPERATURE'):
            config.OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE'))
        
        if os.getenv('MAX_API_CALLS'):
            config.MAX_API_CALLS = int(os.getenv('MAX_API_CALLS'))
        
        if os.getenv('CACHE_ENABLED'):
            config.CACHE_ENABLED = os.getenv('CACHE_ENABLED').lower() == 'true'
        
        if os.getenv('LOG_LEVEL'):
            config.LOG_LEVEL = os.getenv('LOG_LEVEL')
        
        if os.getenv('ALLOW_DANGEROUS_CODE'):
            config.ALLOW_DANGEROUS_CODE = os.getenv('ALLOW_DANGEROUS_CODE').lower() == 'true'
        
        return config
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.PASTA_CREDITO,
            self.PASTA_DEBITO,
            self.PASTA_PROCESSADOS,
            self.PASTA_RELATORIOS,
            self.PASTA_FONTES,
            self.PASTA_CACHE
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        
        # Check if required directories can be created
        try:
            self.ensure_directories()
        except Exception as e:
            errors.append(f"Cannot create directories: {e}")
        
        # Validate AI settings
        if self.OPENAI_TEMPERATURE < 0 or self.OPENAI_TEMPERATURE > 2:
            errors.append("OPENAI_TEMPERATURE must be between 0 and 2")
        
        if self.MAX_API_CALLS < 1:
            errors.append("MAX_API_CALLS must be at least 1")
        
        if self.MAX_INPUT_LENGTH < 10:
            errors.append("MAX_INPUT_LENGTH must be at least 10")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True

# Global configuration instance
config = AppConfig.from_env()

# Validate configuration on import
try:
    config.validate()
except ValueError as e:
    print(f"Configuration error: {e}")
    raise
