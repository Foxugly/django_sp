from tools.generic_views import *
from .models import Pair, Item, Collection, Page, Document
from django.contrib import messages
from django.conf import settings


class DocumentCreateView(GenericCreateView):
    model = Document


class DocumentListView(GenericListView):
    model = Document


class DocumentUpdateView(GenericUpdateView):
    model = Document


class DocumentDetailView(GenericDetailView):
    model = Document
    template_name = 'document_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        context['website'] = obj.ref_website.name
        context['view'] = settings.VIEW_FOR_EXPORT
        return context


class DocumentDeleteView(GenericDeleteView):
    model = Document


class PairCreateView(GenericCreateView):
    model = Pair


class PairListView(GenericListView):
    model = Pair


class PairUpdateView(GenericUpdateView):
    model = Pair


class PairDetailView(GenericDetailView):
    model = Pair


class PairDeleteView(GenericDeleteView):
    model = Pair
    

class ItemCreateView(GenericCreateView):
    model = Item


class ItemListView(GenericListView):
    model = Item


class ItemUpdateView(GenericUpdateView):
    model = Item


class ItemDetailView(GenericDetailView):
    model = Item
    template_name = 'item_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        context['website'] = obj.ref_website.name
        context['view'] = settings.VIEW_FOR_EXPORT
        return context

class ItemDeleteView(GenericDeleteView):
    model = Item


class CollectionCreateView(GenericCreateView):
    model = Collection


class CollectionListView(GenericListView):
    model = Collection


class CollectionUpdateView(GenericUpdateView):
    model = Collection


class CollectionDetailView(GenericDetailView):
    model = Collection


class CollectionDeleteView(GenericDeleteView):
    model = Collection


class PageCreateView(GenericCreateView):
    model = Page


class PageListView(GenericListView):
    model = Page


class PageUpdateView(GenericUpdateView):
    model = Page

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     obj = self.object
    #     messages.info(self.request,
    #               'je viens de <a href=%s>%s</a>' % (obj.ref_website.prefix, obj.ref_website.prefix),
    #               extra_tags='safe')
    #     return context


class PageDetailView(GenericDetailView):
    model = Page
    template_name = 'page_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        messages.info(self.request, 'From : <a href=%s>%s</a>' % (obj.ref_website.prefix, obj.ref_website.prefix),
                  extra_tags='safe')
        context['website'] = obj.ref_website.name
        context['view'] = settings.VIEW_FOR_EXPORT
        return context


class PageDeleteView(GenericDeleteView):
    model = Page
