from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Screencap, Title
from .services import get_popular_tags
from .utils import paginate_queryset, render_with_infinite_scroll


def home(request):
    content_type = request.GET.get("type")
    screencaps = (
        Screencap.objects.select_related("title").prefetch_related("tags").all()
    )
    if content_type:
        screencaps = screencaps.filter(title__type=content_type.upper())

    page_obj, custom_range = paginate_queryset(request, screencaps, 21)

    popular_tags = get_popular_tags()

    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]

    context = {
        "page_obj": page_obj,
        "custom_range": custom_range,
        "popular_tags": popular_tags,
        "extra_params": query_params.urlencode(),
    }

    return render_with_infinite_scroll(request, "gallery/home.html", context)


def search(request):
    query = request.GET.get("q")
    if query:
        screencaps = (
            Screencap.objects.filter(
                Q(tags__name__icontains=query)
                | Q(title__name__icontains=query)
                | Q(title__description__icontains=query)
            )
            .select_related("title")
            .prefetch_related("tags")
            .distinct()
        )
        content_type = request.GET.get("type")
        if content_type and content_type != "all":
            screencaps = screencaps.filter(title__type=content_type.upper())
    else:
        screencaps = Screencap.objects.none()

    page_obj, custom_range = paginate_queryset(request, screencaps, 21)

    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]

    popular_tags = get_popular_tags()

    context = {
        "query": query,
        "page_obj": page_obj,
        "custom_range": custom_range,
        "extra_params": query_params.urlencode(),
        "popular_tags": popular_tags,
    }

    return render_with_infinite_scroll(request, "gallery/search.html", context)


def title_detail(request, slug):
    title = get_object_or_404(Title.objects.prefetch_related("caps"), slug=slug)
    screencaps = title.caps.prefetch_related("tags").all()
    page_obj, custom_range = paginate_queryset(request, screencaps, 21)

    context = {"title": title, "page_obj": page_obj, "custom_range": custom_range}

    return render_with_infinite_scroll(request, "gallery/title_detail.html", context)
