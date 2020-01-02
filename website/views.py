from tools.generic_views import *
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, HttpResponse, redirect
from .models import Website
from page.models import Page, Document, Item
from .tasks import run
import json
import os
import shutil
import urllib
from django.conf import settings
from django.contrib import messages


class WebsiteCreateView(GenericCreateView):
    model = Website


class WebsiteListView(GenericListView):
    model = Website


class WebsiteUpdateView(GenericUpdateView):
    model = Website


class WebsiteDetailView(GenericDetailView):
    model = Website
    template_name = 'website_detail.html'



class WebsiteDeleteView(GenericDeleteView):
    model = Website


class WebsiteRunView(DetailBreadcrumbMixin, TemplateView):
    model = Website
    template_name = 'base.html'
    success_url = reverse_lazy('website:website_list')
    success_message = 'Run complete!'

    def get_context_data(self, *args, **kwargs):
        run(self.kwargs['pk'])
        # run.delay(self.kwargs['pk'])
        context = super(WebsiteRunView, self).get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return self.success_url


class WebsiteExportView(DetailBreadcrumbMixin, TemplateView):
    model = Website
    template_name = 'base.html'
    success_url = reverse_lazy('website:website_list')
    success_message = 'export complete!'

    def get_context_data(self, *args, **kwargs):
        website_export_full(self.kwargs['pk'])
        context = super(WebsiteExportView, self).get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return self.success_url


def website_run_all(request):
    for w in Website.objects.all():
        run(w.pk)
    messages.add_message(request, messages.SUCCESS, 'Import completed !')
    return redirect(reverse_lazy('website:website_list'))


def website_export_all(request):
    for w in Website.objects.all():
        website_export_full(w.pk)
    messages.add_message(request, messages.SUCCESS, 'Export completed !')
    return redirect(reverse_lazy('website:website_list'))


def website_export_json(request, pk):
    w = get_object_or_404(Website, pk=pk)
    file_path = os.path.join(settings.MEDIA_ROOT, '%s.json' % w.name.replace(' ', '_'))
    response = HttpResponse(json.dumps(w.as_json()), content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
    return response


def website_export_full(pk):
    dir_output = os.path.join(settings.BASE_DIR, "output")
    if not os.path.exists(dir_output):
        os.makedirs(dir_output)
    w = get_object_or_404(Website, pk=pk)
    d_website = os.path.join(dir_output, str(w))
    if not os.path.exists(d_website):
        os.makedirs(d_website)
    for page in Page.objects.filter(ref_website=w):
        d_page = os.path.join(d_website, 'page')
        if not os.path.exists(d_page):
            os.makedirs(d_page)
        url = ("http://127.0.0.1:8000/page/page/%s" % page.id)
        webpage = urllib.request.urlopen(url)
        f = open(os.path.join(d_page, '%s.html' % page.id), 'wb')
        f.write(webpage.read())
        f.close()
    for item in Item.objects.filter(ref_website=w):
        d_item = os.path.join(d_website, 'item')
        if not os.path.exists(d_item):
            os.makedirs(d_item)
        url = ("http://127.0.0.1:8000/page/item/%s" % item.id)
        webpage = urllib.request.urlopen(url)
        f = open(os.path.join(d_item, '%s.html' % item.id), 'wb')
        f.write(webpage.read())
        f.close()
    for doc in Document.objects.filter(ref_website=w):
        d_item = os.path.join(d_website, 'document')
        if not os.path.exists(d_item):
            os.makedirs(d_item)
        url = ("http://127.0.0.1:8000/page/document/%s" % doc.id)
        webpage = urllib.request.urlopen(url)
        f = open(os.path.join(d_item, '%s.html' % doc.id), 'wb')
        f.write(webpage.read())
        f.close()
        d_documents = os.path.join(os.path.join(settings.BASE_DIR, "documents"), str(w))
        for x in os.listdir(d_documents):
            src_path = os.path.join(d_documents, str(x))
            dst_path = os.path.join(os.path.join(d_website, "document"), str(x))
            if not os.path.exists(dst_path):
                shutil.copytree(src_path, dst_path)
