from django.db.models import Count
from taggit.models import Tag


def get_popular_tags():
    popular_tags = (
        Tag.objects.filter(
            taggit_taggeditem_items__content_type__model="screencap",
            taggit_taggeditem_items__content_type__app_label="gallery",
        )
        .annotate(total=Count("taggit_taggeditem_items"))
        .order_by("-total")[:10]
    )
    return popular_tags
