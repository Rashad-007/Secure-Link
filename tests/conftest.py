import os
import shutil
import tempfile
import pytest
from app import create_app
from database.db import init_db
from config import Config

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    LOGIN_LOCKOUT_MINUTES = 1
    MAX_FAILED_LOGIN_ATTEMPTS = 3

@pytest.fixture
def app_instance():
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_securelink.db")
    test_storage_dir = os.path.join(temp_dir, "test_storage")

    class RuntimeTestConfig(TestConfig):
        DATABASE_PATH = test_db_path
        STORAGE_DIR = test_storage_dir

    app = create_app(RuntimeTestConfig)

    with app.app_context():
        init_db(test_db_path)

    yield app

    # Cleanup temp directory
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

@pytest.fixture
def runner(app_instance):
    return app_instance.test_cli_runner()

