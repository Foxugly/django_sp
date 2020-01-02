from django.contrib import admin
from .models import Page, Collection, Item, Pair, Document


class PageAdmin(admin.ModelAdmin):
    filter_horizontal = ['collections']


class CollectionAdmin(admin.ModelAdmin):
    filter_horizontal = ['items']


class ItemAdmin(admin.ModelAdmin):
    filter_horizontal = ['pairs', 'documents']


class PairAdmin(admin.ModelAdmin):
    pass


class DocumentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Page, PageAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Pair, PairAdmin)
admin.site.register(Document, DocumentAdmin)
