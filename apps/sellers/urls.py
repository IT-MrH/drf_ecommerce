from django.urls import path

from apps.sellers.views import SellersView, SellerOrderItemView, SellerOrdersView, SellerProductsView, SellerProductView

urlpatterns = [
    path("", SellersView.as_view()),
    path("products/", SellerProductsView.as_view()),
    path("products/<slug:slug>/", SellerProductView.as_view()),
    path("orders/", SellerOrdersView.as_view()),
    path("orders/<str:tx_ref>/", SellerOrderItemView.as_view()),
]
