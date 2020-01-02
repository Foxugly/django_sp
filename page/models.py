from tools.generic_class import GenericClass
from django.db import models
from django.utils.translation import gettext as _


class Document(GenericClass):
    name = models.CharField(max_length=1000, verbose_name=_("name"))
    url = models.CharField(max_length=1000, blank=True, verbose_name=_("url on Sharepoint"))
    local_url = models.CharField(max_length=1000, blank=True, verbose_name=_("url"))
    author = models.CharField(max_length=1000, blank=True, verbose_name=_("author"))
    datetime_creation = models.DateTimeField(null=True, blank=True, verbose_name=_("Datetime Creation"))
    file_size = models.CharField(max_length=10, blank=True, verbose_name=_("Size"))
    file_version = models.CharField(max_length=10, blank=True, verbose_name=_("Version"))
    datetime_modified = models.DateTimeField(null=True, blank=True, verbose_name=_("Datetime Modify"))
    modify_by = models.CharField(max_length=1000, blank=True, verbose_name=_("Modify by"))
    ref_website = models.ForeignKey('website.Website', null=True, on_delete=models.CASCADE)
    ref_item = models.ForeignKey('page.Item', null=True, on_delete=models.CASCADE)

    def get_content(self):
        with open(self.local_url, 'r') as f:
            c = f.read()
        return c

    def as_json(self):
        d = dict(document_id=self.id, name=self.name, url=self.url, local_url=self.local_url, author=self.author,
                 datetime_creation=self.datetime_creation, file_size=self.file_size, file_version=self.file_version,
                 datetime_modified=self.datetime_modified, modify_by=self.modify_by,
                 content=self.get_content())
        return d

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = _('Document')


class Pair(GenericClass):
    key = models.CharField(max_length=100, verbose_name=_("key"))
    value = models.TextField(verbose_name=_("value"))

    def __str__(self):
        return "%s" % self.key

    class Meta:
        verbose_name = _('Pair')


class Item(GenericClass):
    name = models.CharField(max_length=100, verbose_name=_("name"))
    pairs = models.ManyToManyField(Pair, blank=True, verbose_name=_("Pair"))
    documents = models.ManyToManyField(Document, blank=True, verbose_name=_("Document"))
    ref_collection = models.ForeignKey('page.Collection', null=True, on_delete=models.CASCADE)
    ref_website = models.ForeignKey('website.Website', null=True, on_delete=models.CASCADE)

    def as_json(self):
        l_docs = []
        for doc in self.documents.all():
            l_docs.append(doc.as_json())
        d = dict(item_id=self.id, name=self.name.replace('\n', '').replace('\t', ''), documents=l_docs)
        for p in self.pairs.all():
            if p.key not in d:
                d[p.key] = p.value.replace('\n', '').replace('\t', '')
            else:
                print("ERROR")
        return d

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = _('Item')


class Collection(GenericClass):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    ref_website = models.ForeignKey('website.Website', null=True, on_delete=models.CASCADE)
    ref_page = models.ForeignKey('page.Page', null=True, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, blank=True, verbose_name=_("Items"))

    def as_json(self):
        l_items = []
        for i in self.items.all():
            l_items.append(i.as_json())
        return dict(collection_id=self.id, name=self.name.replace('\n', '').replace('\t', ''), documents=l_items)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = _('Collection')


class Page(GenericClass):
    name = models.CharField(max_length=100, verbose_name=_("name"))
    slug = models.SlugField(max_length=100, verbose_name=_("slug"))
    datetime_begin = models.DateTimeField(null=True, blank=True, verbose_name=_("Datetime begin"))
    datetime_end = models.DateTimeField(null=True, blank=True, verbose_name=_("Datetime end"))
    body = models.TextField(verbose_name=_("body"))
    url = models.CharField(max_length=1000, verbose_name=_("url"), null=True, blank=True,)
    collections = models.ManyToManyField(Collection, blank=True, verbose_name=_("Collections"))
    ref_website = models.ForeignKey('website.Website', null=True, on_delete=models.CASCADE)

    def as_json(self):
        l_cols = []
        for col in self.collections.all():
            l_cols.append(col.as_json())
        d = dict(page_id=self.id, name=self.name.replace('\n', '').replace('\t', ''), slug=self.slug,
                 datetime_begin=str(self.datetime_begin) if self.datetime_begin else None,
                 datetime_end=str(self.datetime_end) if self.datetime_end else None,
                 url=self.url, collections=l_cols)
        return d

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = _('Page')
