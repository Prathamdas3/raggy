"""Custom Pydantic base model.

Provides a base model class with common configuration for all Pydantic models.
"""

from pydantic import BaseModel, ConfigDict


class CustomBaseModel(BaseModel):
    """Base model with common configuration.

    Configures populate_by_name to allow field population
    by both alias and original name.
    """

    model_config = ConfigDict(populate_by_name=True)
