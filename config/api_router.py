from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from ksatria_muslim.books.api.views import BookViewSet, BookStateViewSet
from ksatria_muslim.children.api.views import ChildViewSet
from ksatria_muslim.rewards.api.views import RewardHistoryViewSet
from ksatria_muslim.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("books", BookViewSet)
router.register("books-state", BookStateViewSet)
router.register("users", UserViewSet)
router.register("child", ChildViewSet)
router.register("reward-history", RewardHistoryViewSet)


app_name = "api"
urlpatterns = router.urls
