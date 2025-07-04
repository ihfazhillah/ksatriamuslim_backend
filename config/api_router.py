from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from ksatria_muslim.books.api.views import BookViewSet, BookStateViewSet, force_generate_images
from ksatria_muslim.children.api.views import ChildViewSet, PhotoProfileViewSet
from ksatria_muslim.packages.api.views import PackageUsageViewSet
from ksatria_muslim.rewards.api.views import RewardHistoryViewSet
from ksatria_muslim.users.api.views import UserViewSet
from ksatria_muslim.sensors.api.views import log_sensor, ping_device

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
    path("book-tools/force-generate-images/", force_generate_images, name="force-generate-images"),
    path("events/", include("ksatria_muslim.events.urls", namespace="events")),
    path("children-task/", include("ksatria_muslim.children_task.urls")),
    path("kanban/", include("ksatria_muslim.kidskanbantask.urls")),
]

