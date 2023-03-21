from rest_framework.routers import DefaultRouter

from order.views import OrderView

app_name = 'orders'

router = DefaultRouter()
router.register(r'', OrderView)

urlpatterns = router.urls
