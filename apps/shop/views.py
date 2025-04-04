from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from apps.sellers.models import Seller
from apps.shop.models import Category, Product, Review
from apps.shop.filters import ProductFilter, ReviewFilter
from apps.profiles.models import OrderItem, ShippingAddress, Order
from apps.common.permissions import IsSeller, IsOwnerOrReadOnly
from apps.common.paginations import CustomPagination
from apps.shop.schema_examples import PRODUCT_PARAM_EXAMPLE, REVIEW_PARAM_EXAMPLE
from apps.shop.serializers import OrderItemSerializer, ToggleCartItemSerializer, CheckoutSerializer, \
    OrderSerializer, CategorySerializer, ProductSerializer, CreateReviewSerializer, ReviewSerializer
from apps.common.utils import set_dict_attr

tags = ["Shop"]


class CategoriesView(APIView):
    permission_classes = [IsSeller]
    serializer_class = CategorySerializer

    @extend_schema(
        summary="Categories Fetch",
        description="""
            This endpoint returns all categories.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = self.serializer_class(categories, many=True)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Category Creating",
        description="""
            This endpoint creates categories.
        """,
        tags=tags
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_cat = Category.objects.create(**serializer.validated_data)
            serializer = self.serializer_class(new_cat)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class ProductsByCategoryView(APIView):
    permission_classes = [IsSeller]
    serializer_class = ProductSerializer

    @extend_schema(
        operation_id="category_products",
        summary="Category Products Fetch",
        description="""
            This endpoint returns all products in a particular category.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        category = Category.objects.get_or_none(slug=kwargs["slug"])
        if not category:
            return Response(data={"message": "Category does not exist!"}, status=404)
        products = Product.objects.select_related("category", "seller", "seller__user").filter(category=category)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


class ProductsView(APIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    @extend_schema(
        operation_id="all_products",
        summary="Product Fetch",
        description="""
            This endpoint returns all products.
        """,
        tags=tags,
        parameters=PRODUCT_PARAM_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        products = Product.objects.select_related("category", "seller", "seller__user").all()
        filter_set = ProductFilter(request.GET, queryset=products)
        if filter_set.is_valid():
            queryset = filter_set.qs
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(filter_set.errors, status=400)


class ProductsBySellerView(APIView):
    permission_classes = [IsSeller]
    serializer_class = ProductSerializer

    @extend_schema(
        summary="Seller Products Fetch",
        description="""
            This endpoint returns all products in a particular seller.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        seller = Seller.objects.get_or_none(slug=kwargs["slug"])
        if not seller:
            return Response(data={"message": "Seller does not exist!"}, status=404)
        products = Product.objects.select_related("category", "seller", "seller__user").filter(seller=seller)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


class ProductView(APIView):
    permission_classes = [IsSeller]
    serializer_class = ProductSerializer

    def get_object(self, slug):
        product = Product.objects.get_or_none(slug=slug)
        return product

    @extend_schema(
        operation_id="product_detail",
        summary="Product Details Fetch",
        description="""
            This endpoint returns the details for a product via the slug.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        product = self.get_object(kwargs['slug'])
        if not product:
            return Response(data={"message": "Product does not exist!"}, status=404)
        serializer = self.serializer_class(product)
        return Response(data=serializer.data, status=200)


class CartView(APIView):
    permission_classes = [IsSeller]
    serializer_class = OrderItemSerializer

    @extend_schema(
        summary="Cart Items Fetch",
        description="""
            This endpoint returns all items in a user cart.
        """,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        orderitems = OrderItem.objects.filter(user=user, order=None).select_related(
            "product", "product__seller", "product__seller__user")
        serializer = self.serializer_class(orderitems, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Toggle Item in cart",
        description="""
            This endpoint allows a user or guest to add/update/remove an item in cart.
            If quantity is 0, the item is removed from cart
        """,
        tags=tags,
        request=ToggleCartItemSerializer,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ToggleCartItemSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        quantity = data["quantity"]

        product = Product.objects.select_related("seller", "seller__user").get_or_none(slug=data["slug"])
        if not product:
            return Response({"message": "No Product with that slug"}, status=404)
        orderitem, created = OrderItem.objects.update_or_create(
            user=user,
            order_id=None,
            product=product,
            defaults={"quantity": quantity},
        )
        resp_message_substring = "Updated In"
        status_code = 200
        if created:
            status_code = 201
            resp_message_substring = "Added To"
        if quantity == 0:
            resp_message_substring = "Removed From"
            orderitem.delete()
            data = None
        if resp_message_substring != "Removed From":
            serializer = self.serializer_class(orderitem)
            data = serializer.data
        return Response(data={"message": f"Item {resp_message_substring} Cart", "item": data}, status=status_code)


class CheckoutView(APIView):
    permission_classes = [IsSeller]
    serializer_class = CheckoutSerializer

    @extend_schema(
        summary="Checkout",
        description="""
               This endpoint allows a user to create an order through which payment can then be made through.
               """,
        tags=tags,
        request=CheckoutSerializer,
    )
    def post(self, request, *args, **kwargs):
        # Proceed to checkout
        user = request.user
        orderitems = OrderItem.objects.filter(user=user, order=None)
        if not orderitems.exists():
            return Response({"message": "No Items in Cart"}, status=404)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_id = data.get("shipping_id")
        if shipping_id:
            # Получаем информацию о доставке на основе идентификатора доставки, введенного пользователем.
            shipping = ShippingAddress.objects.get_or_none(id=shipping_id)
            if not shipping:
                return Response({"message": "No shipping address with that ID"}, status=404)

        fields_to_update = [
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "zipcode",
        ]
        data = {}
        for field in fields_to_update:
            value = getattr(shipping, field)
            data[field] = value

        order = Order.objects.create(user=user, **data)
        orderitems.update(order=order)

        serializer = OrderSerializer(order)
        return Response(data={"message": "Checkout Successful", "item": serializer.data}, status=200)


class ReviewsView(APIView):
    serializer_class = CreateReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = CustomPagination

    def get_object(self, slug):
        product = Product.objects.get_or_none(slug=slug)
        return product

    @extend_schema(
        operation_id="reviews_product",
        summary="Product reviews",
        description="""
                This endpoint allows the user or guest to receive all product reviews.
            """,
        tags=tags,
        responses=ReviewSerializer,
        parameters=REVIEW_PARAM_EXAMPLE
    )
    def get(self, request, *args, **kwargs):
        product = self.get_object(kwargs["slug"])
        if not product:
            return Response(data={"message": "No Product with that slug"}, status=404)
        reviews = product.review.all()
        filter_set = ReviewFilter(request.query_params, queryset=reviews)
        if filter_set.is_valid():
            queryset = filter_set.qs
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = ReviewSerializer(paginated_queryset, many=True)
            return Response(data=serializer.data, status=200)
        return Response(filter_set.errors, status=400)

    @extend_schema(
        summary="Create Review",
        description="""
                This endpoint creates a review from an authorized user. 
                It is allowed to leave one product review from one user.
            """,
        tags=tags,
        request=CreateReviewSerializer,
        responses=ReviewSerializer,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        product = self.get_object(kwargs["slug"])
        if not product:
            return Response(data={"message": "No Product with that slug"}, status=404)
        serializer = self.serializer_class(data=request.data, context={'product': product, 'user': user})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        review = Review.objects.create(user=user, product=product, **data)
        serializer = ReviewSerializer(review)
        return Response(data=serializer.data, status=201)


class ReviewView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = CreateReviewSerializer

    def get_object(self, review_id):
        review = Review.objects.get_or_none(id=review_id)
        if review is not None:
            self.check_object_permissions(self.request, review)
        return review

    @extend_schema(
        summary="Update Review",
        description="""
                This endpoint allows the user to update their review as well as the administrator.
            """,
        tags=tags,
        request=CreateReviewSerializer,
        responses=ReviewSerializer,

    )
    def put(self, request, *args, **kwargs):
        review = self.get_object(kwargs["id"])
        if not review:
            return Response(data={"message": "Review does not exist!"}, status=404)
        serializer = self.serializer_class(review, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data['rating'] == review.rating and data['text'] == review.text:
            return Response(data={"message": "The review has no changes."}, status=400)
        user_review = set_dict_attr(review, data)
        user_review.save()
        serializer = ReviewSerializer(user_review)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Delete Review",
        description="""
                This endpoint allows a user to delete review.
            """,
        tags=tags,
    )
    def delete(self, request, *args, **kwargs):
        review = self.get_object(kwargs["id"])
        if not review:
            return Response(data={"message": "Review does not exist!"}, status=404)
        review.delete()
        return Response(data={"message": "Review deleted successfully"}, status=200)
