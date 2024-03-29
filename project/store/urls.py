from django.urls import path

from store import views

urlpatterns = [
    path('categories', views.CategoriesListView.as_view()),
    path('categories/<slug:slug>/products', views.ProductListView.as_view()),
    path('categories/<slug:slug>/filter', views.ProductFilterListView.as_view()),
    path('product/create', views.ProductCreateView.as_view()),
    path('product/<slug:slug>', views.ProductDetailView.as_view()),
    path('product/<slug:slug>/add/images', views.AddProductImagesView.as_view()),
    path('product/<slug:slug>/favorite', views.FavoriteProductAddDeleteView.as_view()),
]
