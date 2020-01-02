from django.contrib import admin
from .models import Website
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class WebsiteResource(resources.ModelResource):

    class Meta:
        model = Website
        # fields = '__all__'


class WebsiteAdmin(ImportExportModelAdmin):
    resource_class = WebsiteResource


admin.site.register(Website, WebsiteAdmin)

