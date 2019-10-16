ENVIRONMENT = 'local'
# ENVIRONMENT = 'development'
ENVIRONMENT = 'production'

SETTINGS_MODULE = 'projectx.local'

if ENVIRONMENT == 'development':
    SETTINGS_MODULE = 'projectx.development'
if ENVIRONMENT == 'production':
    SETTINGS_MODULE = 'projectx.production'
