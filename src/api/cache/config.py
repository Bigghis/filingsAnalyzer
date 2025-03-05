# Cache settings
CACHE_ENABLED = True  # Global switch for caching

host = "localhost"
port = 6379
db = 0
socket_timeout = 5
retry_on_timeout = True
max_connections = 10
health_check_interval = 30

# Cache durations
CACHE_EXPIRATION_1HOUR = 3600  # Cache duration in seconds (1 hour)
CACHE_EXPIRATION_1DAY = 86400  # Cache duration in seconds (1 day)
