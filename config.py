import os
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

EMPLOYEES_FILE = DATA_DIR / "employees.json"

SALARY_LEVELS = {
    "L1": 10000,
    "L2": 20000,
    "L3": 35000
}

LOG_FILE = PROJECT_ROOT / "agent_orchestrator.log"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()
