import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Screencap, Title

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class GalleryModelsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.movie = Title.objects.create(name="Test Movie", release_year=2026)
        cls.series = Title.objects.create(
            type=Title.Type.SERIES,
            name="Test TV Show",
            release_year=2021,
            end_year=2025,
        )
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        cls.screencap = Screencap.objects.create(
            title=cls.movie,
            image=SimpleUploadedFile(
                "test.gif", cls.small_gif, content_type="image/gif"
            ),
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


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class GalleryViewsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.movie = Title.objects.create(name="Test Movie", release_year=2026)
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        cls.screencap = Screencap.objects.create(
            title=cls.movie,
            image=SimpleUploadedFile(
                "test.gif", cls.small_gif, content_type="image/gif"
            ),
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

    def test_home_view_filtering(self):
        Title.objects.create(
            name="Test Series", type=Title.Type.SERIES, release_year=2026
        )
        response = self.client.get(reverse("gallery:home", query={"type": "movie"}))
        for cap in response.context["page_obj"]:
            self.assertEqual(cap.title.type, Title.Type.MOVIE)

    def test_popular_tags_in_context(self):
        response = self.client.get(reverse("gallery:home"))
        self._assert_tag_in_popular(response, "horror")
        response = self.client.get(reverse("gallery:search", query={"q": ""}))
        self._assert_tag_in_popular(response, "horror")
        response = self.client.get(reverse("gallery:search", query={"q": "comedy"}))
        self._assert_tag_in_popular(response, "horror")

    def test_search_with_type_filter(self):
        url = reverse("gallery:search", query={"q": "horror", "type": "series"})
        response = self.client.get(url)
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_home_infinite_scroll(self):
        url = reverse("gallery:home")
        response = self.client.get(url)
        self.assertContains(response, "<h1>Latest Screencaps</h1>")
        self.assertTemplateUsed(response, "gallery/home.html")
        response = self.client.get(url, HTTP_HX_REQUEST="true")
        self.assertNotContains(response, "</nav>")
        self.assertContains(response, 'class="pswp-link"')
        self.assertNotContains(response, "<h1>Latest Screencaps</h1>")
        self.assertTemplateUsed(response, "gallery/includes/_screencaps_loop.html")

    def test_home_shuffle_functional(self):
        for _ in range(5):
            Screencap.objects.create(
                title=self.movie,
                image=SimpleUploadedFile(
                    "test.gif", self.small_gif, content_type="image/gif"
                ),
            )
        response = self.client.get(reverse("gallery:home", query={"sort": "shuffle"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 6)
        self.assertContains(response, "btn-light rounded-pill shadow-sm")
        self.assertContains(response, "Reset Shuffle")

    def test_about_view(self):
        url = reverse("about")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("gallery/about.html")
        self.assertContains(response, "GitHub")

    def test_custom_404_template(self):
        response = self.client.get("/this-is-a-fake-url-12345/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def _assert_tag_in_popular(self, response, tag_name):
        self.assertIn("popular_tags", response.context)
        tags_in_context = [tag.name for tag in response.context["popular_tags"]]
        self.assertIn(tag_name, tags_in_context)
