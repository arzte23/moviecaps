from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from taggit.models import Tag

from .models import Screencap, Title


def home(request):
    content_type = request.GET.get("type")
    screencaps = Screencap.objects.select_related("title").all()
    if content_type:
        screencaps = screencaps.filter(title__type=content_type.upper())
    paginator = Paginator(screencaps, 21)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    custom_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )
    popular_tags = (
        Tag.objects.filter(
            taggit_taggeditem_items__content_type__model="screencap",
            taggit_taggeditem_items__content_type__app_label="gallery",
        )
        .annotate(total=Count("taggit_taggeditem_items"))
        .order_by("-total")[:10]
    )
    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]

    return render(
        request,
        "gallery/home.html",
        {
            "page_obj": page_obj,
            "custom_range": custom_range,
            "popular_tags": popular_tags,
            "extra_params": query_params.urlencode(),
        },
    )


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
            .distinct()
        )
    else:
        screencaps = Screencap.objects.none()

    paginator = Paginator(screencaps, 21)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    custom_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )
    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]

    return render(
        request,
        "gallery/search.html",
        {
            "query": query,
            "page_obj": page_obj,
            "custom_range": custom_range,
            "extra_params": query_params.urlencode(),
        },
    )


def title_detail(request, slug):
    title = get_object_or_404(Title.objects.prefetch_related("caps"), slug=slug)
    screencaps = title.caps.all()
    paginator = Paginator(screencaps, 21)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    custom_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )
    return render(
        request,
        "gallery/title_detail.html",
        {"title": title, "page_obj": page_obj, "custom_range": custom_range},
    )
