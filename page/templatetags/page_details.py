from django import template
import re

register = template.Library()


@register.filter()
def get_title(item):
    if "Document Library" in item.name:
        return item.name.split(' - ')[2]
    out = None
    name = None
    if item:
        for p in item.pairs.all():
            if p.key == "Title":
                out = p.value
            if p.key == "Name":
                name = p.value
    if not out:
        if name:
            out = name
        else:
            out = "Not found"
    return out


@register.filter()
def cast_url(s):
    out = s.replace('\\', '/')
    return out


@register.filter()
def cast_local(s):
    path = s.split('\\')
    out = '../document/%s/%s' % (path[2], path[3])
    return out


@register.filter()
def get_value(item, key):
    if item:
        pair = item.pairs.filter(key=key)
        return pair[0].value if len(pair) else None
    return None


@register.filter()
def get_doc(item):
    return item.documents.all()[0]


@register.filter()
def get_doc_id(item):
    return item.documents.all()[0].id


@register.filter()
def get_author(doc):
    return doc.author


@register.filter()
def get_datetime_modified(doc):
    return doc.datetime_modified


@register.filter()
def get_modify_by(doc):
    return doc.modify_by
