from django.urls import path

from order import views

urlpatterns = [
    path('', views.OrderListCreateView.as_view()),
    path('<int:pk>', views.OrderDetailView.as_view()),
    path('paycallback', views.PayCallbackView.as_view()),
]
