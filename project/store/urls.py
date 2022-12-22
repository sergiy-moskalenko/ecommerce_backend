from django.urls import path

from store import views

urlpatterns = [
    path('categories', views.CategoriesListView.as_view()),
    path('categories/<slug:slug>/products', views.ProductListView.as_view()),
    path('product/<slug:slug>', views.ProductDetailView.as_view()),
    path('product/create', views.ProductCreateView.as_view()),
    path('product/favorite/<slug:slug>', views.FavoriteProductAddDeleteView.as_view()),
]
