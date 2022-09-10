import os
import pytest



test_data_folder = os.path.dirname(__file__)
def pytest_configure():
    pytest.TEST_DATABASE_FOLDER = os.path.join(test_data_folder, "./TestData")

@pytest.fixture
def master_data():
    test_data_file = os.path.join(test_data_folder, "./TestData/broker.master")
    try:
        f = open(test_data_file, "rb")
        binfile = f.read()
    finally:
        f.close()
    return binfile

@pytest.fixture
def index_db():
    return os.path.join(test_data_folder, "./TestDB")


@pytest.fixture
def symbol_spce():
    test_data_file = os.path.join(test_data_folder, "./TestData/s/SPCE")
    try:
        f = open(test_data_file, "rb")
        binfile = f.read()
    finally:
        f.close()
    return binfile





