from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
from core import settings

PRODUCT_PARAM_EXAMPLE = [
    OpenApiParameter(
        name="max_price",
        description="Filter products by MAX current price",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="min_price",
        description="Filter products by MIN current price",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="in_stock",
        description="Filter products by stock",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="created_at",
        description="Filter products by date created",
        required=False,
        type=OpenApiTypes.DATE,
    ),
    OpenApiParameter(
        name="page",
        description="Retrieve a particular page. Defaults to 1",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="page_size",
        description=f"The amount of item per page you want to display. Defaults to {settings.REST_FRAMEWORK['PAGE_SIZE']}",
        required=False,
        type=OpenApiTypes.INT,
    ),
]

REVIEW_PARAM_EXAMPLE = [
    OpenApiParameter(
        name="min_rating",
        description="Filter review by MIN rating",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="max_rating",
        description="Filter review by MAX rating",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="created_at",
        description="Filter review by date created",
        required=False,
        type=OpenApiTypes.DATE,
    ), OpenApiParameter(
        name="ordering_rating",
        description="Filter rating(increase, decrease)",
        required=False,
        type=OpenApiTypes.DATE,
    ), OpenApiParameter(
        name="ordering_created",
        description="Filter data create(increase, decrease)",
        required=False,
        type=OpenApiTypes.DATE,
    ),
    OpenApiParameter(
        name="page_size",
        description=f"The amount of item per page you want to display. Defaults to {settings.REST_FRAMEWORK['PAGE_SIZE']}",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="page",
        description="Retrieve a particular page. Defaults to 1",
        required=False,
        type=OpenApiTypes.INT,
    ),
]
