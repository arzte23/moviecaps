from django.test import TestCase
from django.urls import reverse

from .models import Screencap, Title


class GalleryModelsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie = Title.objects.create(name="Test Movie", release_year=2026)
        cls.series = Title.objects.create(
            type=Title.Type.SERIES,
            name="Test TV Show",
            release_year=2021,
            end_year=2025,
        )
        cls.screencap = Screencap.objects.create(
            title=cls.movie, image="screencaps/test.jpg", width=200, height=200
        )
        cls.screencap.tags.add("horror", "christmas", "clown")

    def test_title_model(self):
        self.assertEqual(self.movie.type.label, "Movie")
        self.assertEqual(self.movie.name, "Test Movie")
        self.assertEqual(self.movie.slug, "test-movie-2026")
        self.assertEqual(self.movie.release_year, 2026)
        self.assertEqual(str(self.movie), "Test Movie (2026)")
        self.assertEqual(self.series.type.label, "TV Show")
        self.assertEqual(str(self.series), "Test TV Show (2021 - 2025)")

    def test_screencap_model(self):
        self.assertEqual(self.screencap.title.name, "Test Movie")
        self.assertIn("clown", self.screencap.tags.names())
        self.assertEqual(str(self.screencap), "Screencap from Test Movie (2026)")
        self.assertIn(self.screencap, self.movie.caps.all())


class GalleryViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie = Title.objects.create(name="Test Movie", release_year=2026)
        cls.screencap = Screencap.objects.create(
            title=cls.movie, image="screencaps/test.jpg", width=200, height=200
        )
        cls.screencap.tags.add("horror", "christmas", "clown")

    def test_home_view(self):
        response = self.client.get(reverse("gallery:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gallery/home.html")
        self.assertIn(self.screencap, response.context["page_obj"])
        self.assertContains(response, self.screencap.image.url)

    def test_search_view_success(self):
        response = self.client.get(reverse("gallery:search", query={"q": "horror"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.screencap.image.url)

    def test_search_view_no_results(self):
        response = self.client.get(reverse("gallery:search", query={"q": "comedy"}))
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_search_view_empty_query(self):
        response = self.client.get(reverse("gallery:search", query={"q": ""}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_title_detail_view_success(self):
        response = self.client.get(
            reverse("gallery:title_detail", args=[self.movie.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.movie.name)
        self.assertTemplateUsed(response, "gallery/title_detail.html")

    def test_title_detail_view_404(self):
        response = self.client.get(reverse("gallery:title_detail", args=["wrong-slug"]))
        self.assertEqual(response.status_code, 404)
