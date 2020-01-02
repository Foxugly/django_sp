from django import template

register = template.Library()


@register.filter()
def get_pages_sorted(website):
    return website.pages.all().order_by('datetime_begin')

