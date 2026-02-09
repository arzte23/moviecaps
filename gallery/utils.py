def title_slug(instance):
    return f"{instance.name} {str(instance.release_year)}"
