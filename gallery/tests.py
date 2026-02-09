from django.test import TestCase

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
            title=cls.movie, image="screencaps/test.jpg"
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
