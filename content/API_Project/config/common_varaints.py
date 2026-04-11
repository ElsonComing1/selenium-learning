# common_varaints.py
from pathlib import Path

# dir
PROJECT_DIR = Path(__file__).parent.parent
API_DIR = PROJECT_DIR / 'api'
CONFIG_DIR = PROJECT_DIR / 'config'
CORE_DIR = PROJECT_DIR / "core"
DATA_DIR = PROJECT_DIR / "data"
LOGS_DIR = PROJECT_DIR / 'logs'
ERROR_LOGS_DIR = LOGS_DIR / 'error_logs'
TESTCASES_DIR = PROJECT_DIR / "testcases"
UTILS_DIR = PROJECT_DIR / "utils"

# file
ENV_SETTINGS_FILE=CONFIG_DIR / 'env_settings.yaml'
TEST_CASES_FILE=DATA_DIR / 'test_cases.json'