from core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": [
                "models.item_model",
                "models.item_photo_model",
                "models.item_variant_model",
                "models.category_model",
                "models.attribute_model",
                "aerich.models",
            ],
            "default_connection": "default",
            "migrations": "models.migrations",
        },
    },
}