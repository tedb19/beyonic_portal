from .base import *

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the user_account app
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=user_account',
    '--verbosity=2',
]