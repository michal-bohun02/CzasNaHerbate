from core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["models.item_model", "aerich.models"],
            "default_connection": "default",
        },
    },
}