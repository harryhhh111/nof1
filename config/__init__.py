# -*- coding: utf-8 -*-
"""
Configuration module

Export original config and multi-account config
"""

# Import original config (from parent package)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config as original_config

# Re-export original config
UPDATE_INTERVAL = original_config.UPDATE_INTERVAL
DATABASE_PATH = original_config.DATABASE_PATH
SYMBOLS = original_config.SYMBOLS
INTERVALS = original_config.INTERVALS
INDICATOR_PARAMS = original_config.INDICATOR_PARAMS
TABLES = original_config.TABLES
BINANCE_API_KEY = original_config.BINANCE_API_KEY
BINANCE_SECRET_KEY = original_config.BINANCE_SECRET_KEY
USE_TESTNET = original_config.USE_TESTNET
DEMO_API_KEY = original_config.DEMO_API_KEY
DEMO_SECRET_KEY = original_config.DEMO_SECRET_KEY
TESTNET_API_KEY = original_config.TESTNET_API_KEY
TESTNET_SECRET_KEY = original_config.TESTNET_SECRET_KEY
CURRENT_MODE = original_config.CURRENT_MODE
TRADING_MODE = original_config.TRADING_MODE
LOG_LEVEL = original_config.LOG_LEVEL
LOG_FORMAT = original_config.LOG_FORMAT
ACCOUNT_CONFIGS = original_config.ACCOUNT_CONFIGS
LLM_MODEL_PRIORITY = original_config.LLM_MODEL_PRIORITY
MULTI_ACCOUNT_COMPARISON = original_config.MULTI_ACCOUNT_COMPARISON

# Export multi-account config
from .traders_config import (
    TRADERS_CONFIG,
    LLM_MODELS_CONFIG,
    SYSTEM_CONFIG,
    CUSTOM_PROMPTS,
    get_traders_config,
    get_llm_models_config,
    get_system_config,
    get_custom_prompts,
    validate_config,
    print_config_summary
)

__all__ = [
    # Original config
    'UPDATE_INTERVAL',
    'DATABASE_PATH',
    'SYMBOLS',
    'INTERVALS',
    'INDICATOR_PARAMS',
    'TABLES',
    'BINANCE_API_KEY',
    'BINANCE_SECRET_KEY',
    'USE_TESTNET',
    'DEMO_API_KEY',
    'DEMO_SECRET_KEY',
    'TESTNET_API_KEY',
    'TESTNET_SECRET_KEY',
    'CURRENT_MODE',
    'TRADING_MODE',
    'LOG_LEVEL',
    'LOG_FORMAT',
    'ACCOUNT_CONFIGS',
    'LLM_MODEL_PRIORITY',
    'MULTI_ACCOUNT_COMPARISON',
    # Multi-account config
    'TRADERS_CONFIG',
    'LLM_MODELS_CONFIG',
    'SYSTEM_CONFIG',
    'CUSTOM_PROMPTS',
    'get_traders_config',
    'get_llm_models_config',
    'get_system_config',
    'get_custom_prompts',
    'validate_config',
    'print_config_summary'
]

