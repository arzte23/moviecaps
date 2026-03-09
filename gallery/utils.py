from django.core.paginator import Paginator
from django.shortcuts import render


def title_slug(instance):
    return f"{instance.name} {str(instance.release_year)}"


def paginate_queryset(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    custom_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )
    return page_obj, custom_range


def render_with_infinite_scroll(request, template, context):
    if request.headers.get("HX-Request"):
        return render(
            request,
            "gallery/includes/_screencaps_loop.html",
            context,
        )

    else:
        return render(
            request,
            template,
            context,
        )
