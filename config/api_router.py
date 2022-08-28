from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from ksatria_muslim.books.api.views import BookViewSet, BookStateViewSet, force_generate_images
from ksatria_muslim.children.api.views import ChildViewSet, PhotoProfileViewSet
from ksatria_muslim.packages.api.views import PackageUsageViewSet
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
router.register("photo-profile", PhotoProfileViewSet)
router.register("reward-history", RewardHistoryViewSet)
router.register("package-usage", PackageUsageViewSet)


app_name = "api"
urlpatterns = router.urls + [
    path("books/force-generate-images/", force_generate_images, name="force-generate-images"),
]
