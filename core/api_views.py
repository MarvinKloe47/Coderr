from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoView(APIView):
    """Return public aggregate counts used by the Coderr landing page."""

    permission_classes = [AllowAny]

    def get(self, request):
        average = Review.objects.aggregate(value=Avg("rating"))["value"] or 0
        data = {
            "offer_count": Offer.objects.count(),
            "review_count": Review.objects.count(),
            "business_profile_count": get_user_model()
            .objects.filter(type="business")
            .count(),
            "average_rating": round(average, 1),
        }
        return Response(data)
