from django.core.paginator import Paginator


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
