from tools.generic_class import GenericClass
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from page.models import Page


instance_type = (
    ('date', _('date')),
    ('int', _('entier')),
)


class Website(GenericClass):
    name = models.CharField(max_length=100, verbose_name=_("name"))
    running = models.BooleanField(default=False)
    url = models.CharField(max_length=1000, verbose_name=_("url"))
    instance_id_type = models.CharField(_("InstanceId type"), max_length=4, choices=instance_type, default=1)
    prefix = models.CharField(max_length=500, verbose_name=_("prefix"))
    pages = models.ManyToManyField(Page, blank=True, verbose_name=_("Pages"))
    date_start = models.DateField(null=True, blank=True, verbose_name=_("start of date"))
    date_limit = models.DateField(null=True, blank=True, verbose_name=_("Limit of date"))
    id_limit = models.IntegerField(default=100, null=True, blank=True, verbose_name=_("id max"))

    def as_json(self):
        l_pages = []
        for page in self.pages.all():
            l_pages.append(page.as_json())
        return dict(website_id=self.id, name=self.name, pages=l_pages)

    def get_run_url(self):
        return reverse('website:website_run', kwargs={'pk': self.pk})

    def get_export_json_url(self):
        return reverse('website:website_export_json', kwargs={'pk': self.pk})

    def get_export_full_url(self):
        return reverse('website:website_export_full', kwargs={'pk': self.pk})

    def get_links(self):
        out = [{'text': "Add", 'url': self.get_add_url, 'icon': "fa-plus", 'btn': 'btn-primary'},
               {'text': "Aspire all websites", 'url': reverse('website:website_run_all'), 'icon': "fa-gear", 'btn': 'btn-info'},
               {'text': "Export all websites", 'url': reverse('website:website_export_all'), 'icon': "fa-gears", 'btn': 'btn-warning'}
               ]
        return out

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Website')
