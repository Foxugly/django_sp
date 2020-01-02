import csv
from website.models import Website

fields = ["name", "url", "instance_id_type", "prefix", "date_start", "date_limit", "id_limit"]


with open('website.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fields)
    for obj in Website.objects.all():
        row = writer.writerow([getattr(obj, str(field)) for field in fields])
