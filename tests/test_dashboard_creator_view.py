from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.marketplace.models import Asset, Purchase
from apps.users.models import User


class CreatorDashboardRenderTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(
            username="creator_case",
            email="creator_case@example.com",
            password="StrongPass123!",
        )
        self.creator.profile.role = "CREATOR"
        self.creator.profile.save()

        self.buyer = User.objects.create_user(
            username="buyer_case",
            email="buyer_case@example.com",
            password="StrongPass123!",
        )

        asset_file = SimpleUploadedFile("asset.txt", b"asset payload", content_type="text/plain")
        self.asset = Asset.objects.create(
            seller=self.creator,
            title="Dungeon Pack",
            description="A modular dungeon asset pack",
            asset_type="3d_model",
            price="29.99",
            file=asset_file,
            is_active=True,
            downloads=42,
            rating=4.5,
        )

        Purchase.objects.create(
            buyer=self.buyer,
            asset=self.asset,
            price_paid="29.99",
        )

    def test_creator_dashboard_shows_asset_title_and_status(self):
        self.client.force_login(self.creator)
        response = self.client.get(reverse("dashboard:overview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Creator Dashboard")
        self.assertContains(response, "Dungeon Pack")
        self.assertContains(response, "Published")
        self.assertContains(response, "buyer_case")
