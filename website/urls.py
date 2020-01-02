from tools.generic_urls import add_url_from_generic_views
from website.views import WebsiteRunView, website_export_json, WebsiteExportView, website_export_all, website_run_all
from django.urls import path

app_name = 'website'
urlpatterns = [
    path('website/run/<int:pk>/', WebsiteRunView.as_view(), name="website_run"),
    path('website/json/<int:pk>/', website_export_json, name="website_export_json"),
    path('website/export/<int:pk>/', WebsiteExportView.as_view(), name="website_export_full"),
    path('website/all/run/', website_run_all, name="website_run_all"),
    path('website/all/export/', website_export_all, name="website_export_all"),

] + add_url_from_generic_views('website.views')
