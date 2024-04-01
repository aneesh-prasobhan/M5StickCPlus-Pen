try:
    Import("env")
except NameError:
    # Define env as None or a mock object for linting purposes
    env = None

import configparser

def load_user_config():
    config = configparser.ConfigParser()
    config.read('platformio_user.ini')
    if 'env:m5stick-c' in config and 'lib_extra_dirs' in config['env:m5stick-c']:
        lib_dirs = config['env:m5stick-c']['lib_extra_dirs']
        env.Append(LIB_EXTRA_DIRS=[lib_dirs])

load_user_config()
