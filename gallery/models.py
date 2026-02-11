from autoslug import AutoSlugField
from django.db import models
from taggit.managers import TaggableManager

from .utils import title_slug


class Title(models.Model):
    class Type(models.TextChoices):
        MOVIE = "MOVIE", "Movie"
        SERIES = "SERIES", "TV Show"

    type = models.CharField(max_length=10, choices=Type, default=Type.MOVIE)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    release_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField(blank=True, null=True)
    slug = AutoSlugField(populate_from=title_slug, unique=True)

    def __str__(self):
        if self.end_year:
            return f"{self.name} ({self.release_year} - {self.end_year})"
        return f"{self.name} ({self.release_year})"


class Screencap(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name="caps")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to="screencaps/", width_field="width", height_field="height"
    )
    width = models.PositiveIntegerField(editable=False, null=True)
    height = models.PositiveIntegerField(editable=False, null=True)
    tags = TaggableManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Screencap from {self.title}"
