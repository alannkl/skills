import redis

client = None


def init_app(app):
    global client
    client = redis.Redis.from_url(app.config.get("REDIS_URL", "redis://redis:6379/0"))
