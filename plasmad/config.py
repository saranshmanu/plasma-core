# REST API Config
REST_API_HOST = '0.0.0.0'
REST_API_PORT = 8196

# MongoDB Config
MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_DB = 'plasma'
MONGODB_AUTH = False
MONGODB_USER = None
MONGODB_PASSWD = None
MONGODB_AUTH_DATABASE = None

if MONGODB_AUTH is True:
    MONGODB_CONNECTION_URI = 'mongodb://%s:%s@%s:%s/%s?authSource=%s' % (
        MONGODB_USER, MONGODB_PASSWD, MONGODB_HOST, MONGODB_PORT, MONGODB_DB, MONGODB_AUTH_DATABASE)
else:
    MONGODB_CONNECTION_URI = 'mongodb://%s:%s/%s' % (
        MONGODB_HOST, MONGODB_PORT, MONGODB_DB)

# Redis Config
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

# WXE config
EXECUTION_CONTEXT = 'celery'

# Logging Config
LOG_PATH = 'plasma.log'
