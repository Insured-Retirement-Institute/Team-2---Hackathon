"""FastAPI application package."""

__version__ = "0.1.0"

from api.sureify_models import (
    PolicyData,
    PolicyFeaturesData,
    PolicyFeature,
    SuitabilityData,
    DisclosureItem,
    ProductOption,
    VisualizationProduct,
    ClientProfile,
    ComparisonParameters,
)

__all__ = [
    "PolicyData",
    "PolicyFeaturesData",
    "PolicyFeature",
    "SuitabilityData",
    "DisclosureItem",
    "ProductOption",
    "VisualizationProduct",
    "ClientProfile",
    "ComparisonParameters",
]
