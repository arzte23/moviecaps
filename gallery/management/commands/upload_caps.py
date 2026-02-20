from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from gallery.models import Screencap, Title


class Command(BaseCommand):
    help = "Uploads multiple screencaps in one title"

    def add_arguments(self, parser):
        parser.add_argument("name")
        parser.add_argument("year", type=int)
        parser.add_argument("path")

    def handle(self, *args, **options):
        name = options["name"]
        year = options["year"]
        p = Path(options["path"])
        try:
            title = Title.objects.get(name=name, release_year=year)
        except Title.DoesNotExist:
            raise CommandError(f'Title "{name}" does not exist')

        for item in p.iterdir():
            if item.is_file() and item.name.lower().endswith(
                (".jpg", ".png", ".jpeg", ".webp")
            ):
                with open(item, "rb") as f:
                    screenshot = Screencap(title=title)
                    screenshot.image.save(item.name, File(f), save=True)
                    self.stdout.write(f"Success: {item.name} uploaded")
