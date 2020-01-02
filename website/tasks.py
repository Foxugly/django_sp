# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import getpass
import json
import os
import urllib.parse as urlparse
import pytz
import requests
import unidecode
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth
from datetime import datetime, timedelta
from page.models import Page, Collection, Item, Pair, Document
# from ..celery import app
from .models import Website


PASSWORD = getpass.getpass()
#PASSWORD = "123456"
USERNAME = "YOURICT\\RDV"
auth = HttpNtlmAuth(USERNAME, PASSWORD)

debug = False


def format(s):
    print("FORMAT")
    return unidecode.unidecode(s).replace(" ", "_")


list_replace = [('é', '%c3%a9'), ('é', '%C3%A9'), ('ö', '%C3%B6'), (' ', '%20')]
list_user = ["Author", "Editor", ]


def parse(current_url):
    for old, new in list_replace:
        current_url = current_url.replace(old, new)
    return current_url


def unparse(current_url):
    for new, old in list_replace:
        current_url = current_url.replace(old, new)
    return current_url


def get_datetime(date, hour):
    d, m, y = date.replace('"', '').split('/')
    h, m2 = hour.replace('"', '').split(':')
    return datetime(int(y), int(m), int(d), int(h), int(m2), 0, 0, pytz.timezone('Etc/GMT+1'))


def get_user_from_string(value):
    if ";;" in value:
        value = value.split(";;")[1].split(',')[0].replace('#', '')
    return unidecode.unidecode(value)


def manage_key_value(key, value):
    if key in list_user:
        value = get_user_from_string(value)
    elif key == "Notes":
        value = BeautifulSoup(value, "lxml").text
    elif key == "_UIVersionString":
        key = "Version"
    elif key == "Order0":
        key = "Order"
    elif key == "ii_x002e__x0009_Document_x0028_s":
        key = "Document"
    return key, value


exclude = ['https://collab-famhp.yourict.be/entities/CEO/Management/ComDir/Comdir%20POC%20Meeting/'
           'Access%20Requests/pendingreq.aspx', ]


class ParserHtml:
    url = None
    list_visited_url = []
    list_url = []

    def __init__(self, w,):
        self.website = w
        self.name = w.name
        self.url = w.url
        self.prefix = w.prefix
        self.folder = self.name
        self.p_name = None

    def run(self):
        url = self.url[0:self.url.find("InstanceID")]
        if self.website.instance_id_type == "date":
            min_val = self.website.date_start
            while min_val < self.website.date_limit:
                print("%s / %s " % (min_val,self.website.date_limit))
                new_url = url + "InstanceID=%s" % min_val.strftime("%Y%m%d")
                self.extract_data_url(new_url, 0)
                min_val += timedelta(days=1)
        elif self.website.instance_id_type == "int":
            for i in range(1, self.website.id_limit+1):
                print(" %s / %s" % (i, self.website.id_limit+1))
                new_url = url + "InstanceID=%d" % i
                self.extract_data_url(new_url, 0)

    def get_links(self, anchor):
        if "MtgNavigate" in anchor['href']:
            date = str(anchor['href'].split('"')[3])
            new_url = "%sdefault.aspx?InstanceID=" % self.prefix
            link = parse(new_url + date)
        elif "javascript:" in anchor['href']:
            return None
        elif "#" in anchor['href'] and len(anchor['href']) < 2:
            return None
        elif anchor['href'].startswith('/entities/'):
            new_url = anchor['href'].replace('/entities/', 'https://collab-famhp.yourict.be/entities/')
            link = parse(new_url)
        else:
            link = parse(anchor['href'])
        return link

    @staticmethod
    def adjust_sp_url(adr):
        if '/entities/' in adr:
            url_sp = adr.replace('/entities/', 'https://collab-famhp.yourict.be/entities/')
        elif '/KC/' in adr:
            url_sp = adr.replace('/KC/', 'https://collab-famhp.yourict.be/KC/')
        elif '/SPDEV/' in adr:
            url_sp = adr.replace('/SPDEV/', 'https://collab-famhp.yourict.be/SPDEV/')
        return url_sp

    @staticmethod
    def download_document(local_url, url):
        assert os.path.exists(url)
        local_dir = os.path.dirname(local_url)
        main_folder_dir = os.path.dirname(local_dir)
        if not os.path.exists(main_folder_dir):
            try:
                os.mkdir(main_folder_dir)
            except OSError:
                print("Creation of the directory %s failed" % main_folder_dir)
            else:
                print("Successfully created the directory %s " % main_folder_dir)
        if not os.path.exists(local_dir):
            try:
                os.mkdir(local_dir)
            except OSError:
                print("Creation of the directory %s failed" % local_dir)
            else:
                print("Successfully created the directory %s " % local_dir)
        r = requests.get(url, allow_redirects=True, auth=auth)
        with open(local_url, 'wb') as f:
            f.write(r.content)
        assert os.path.exists(local_url)

    def extract_document_library(self, c):
        doc_url = self.prefix + 'Document%20Library/Forms/AllItems.aspx?InstanceID=' + self.p_name
        soup2 = BeautifulSoup(requests.get(doc_url, auth=auth).content, features="html.parser")
        for tr in soup2.find("table", {"id": "onetidDoclibViewTbl0"}).findAll("tr", {"class": "ms-itmhover"}):
            data = tr.findAll("td")
            adr = tr.find("a")['href']
            if adr.split('.')[-1] in ['asp', 'aspx', 'html', 'html5', 'php', 'php3']:
                print("extract_document_library : LINK (asp, aspx, html, html5, ...) : %s" % adr)
                name = adr.split('/')[-1]
                i, i_created = Item.objects.get_or_create(name=name, ref_website=self.website, ref_collection=c)
                if i_created:
                    i.save()
                if i not in c.items.all():
                    c.items.add(i)
                    c.save()
                assert i in c.items.all()
                d, d_created = Document.objects.get_or_create(name=name, url=self.adjust_sp_url(adr),
                                                              local_url=self.adjust_sp_url(adr),
                                                              ref_website=self.website, ref_item=i)
            else:
                print("extract_document_library : DOCUMENT : %s" % adr)
                url_sp = self.adjust_sp_url(adr)
                url = parse(url_sp)
                local_url = os.path.join("documents", self.website.name, self.p_name, url_sp.split('/')[-1])
                i, i_created = Item.objects.get_or_create(name="%s" % data[2].text, ref_website=self.website,
                                                          ref_collection=c)
                if i_created:
                    i.save()
                if i not in c.items.all():
                    c.items.add(i)
                    c.save()
                assert i in c.items.all()
                self.download_document(local_url, url)
                d, d_created = Document.objects.get_or_create(name=url_sp.split('/')[-1], url=url, local_url=local_url,
                                                              ref_website=self.website, ref_item=i)
            if data[4]:
                d.author = data[4].text
            if data[10]:
                d.modify_by = data[10].text
            if data[7]:
                d.file_size = data[7].text
            if data[8]:
                d.file_version = data[8].text
            timezone = pytz.timezone("Etc/GMT+1")
            if len(data) > 10:
                if len(data[6].text) > 10:
                    d.datetime_creation = timezone.localize(datetime.strptime(data[6].text, "%d/%m/%Y %H:%M"))
            if len(data) > 10:
                if len(data[9].text) > 10:
                    d.datetime_modified = timezone.localize(datetime.strptime(data[9].text, "%d/%m/%Y %H:%M"))
            if d_created:
                d.save()
            if d not in i.documents.all():
                i.documents.add(d)
                i.save()
            assert d in i.documents.all()

    def extract_document(self, doc_url, i):
        soup2 = BeautifulSoup(requests.get(doc_url, auth=auth).content, features="html.parser")
        data = str(soup2)
        i_begin = data.find('{"ListData')
        i_end = data.find('};', i_begin) + 1
        dict_data = json.loads(str(soup2)[i_begin: i_end])
        url_document = 'https://collab-famhp.yourict.be%s' % dict_data["ListData"]["FileLeafRef"]["FileUrl"]
        name = dict_data["ListData"]["FileLeafRef"]["BaseName"]
        url = url_document
        local_url = os.path.join("documents", self.website.name, self.p_name, name)
        self.download_document(local_url, url)
        d, created = Document.objects.get_or_create(name=name, url=url, local_url=local_url,
                                                    ref_website=self.website, ref_item=i)
        if dict_data["ListData"]["Author"]:
            d.author = get_user_from_string(dict_data["ListData"]["Author"])
        if dict_data["ListData"]["Editor"]:
            d.modify_by = get_user_from_string(dict_data["ListData"]["Editor"])
        if dict_data["ListData"]["_UIVersionString"]:
            d.file_version = dict_data["ListData"]["_UIVersionString"]
        timezone = pytz.timezone("Etc/GMT+1")
        if dict_data["ListData"]["Created"]:
            d.datetime_creation = timezone.localize(datetime.strptime(dict_data["ListData"]["Created"], "%d/%m/%Y %H:%M"))
        if dict_data["ListData"]["Modified"]:
            d.datetime_modified = timezone.localize(datetime.strptime(dict_data["ListData"]["Modified"], "%d/%m/%Y %H:%M"))
        d.save()
        if d not in i.documents.all():
            i.documents.add(d)
            i.save()
        assert d in i.documents.all()

    def extract_site_users(self, c, body):
        div = body.find("div", {"id": "WebPartWPQ9"})
        if div:
            table = div.find("table")
            for tr in table.findAll("tr"):
                td = tr.findAll("td")[-1]
                a = td.findAll("a")
                if len(a):
                    i, created = Item.objects.get_or_create(name="%s" % a[0].text, ref_website=self.website,
                                                            ref_collection=c)
                    if created:
                        i.save()
                    if i not in c.items.all():
                        c.items.add(i)
                        c.save()
                    assert i in c.items.all()
                    p, created = Pair.objects.get_or_create(key="Name", value=a[0].text)
                    if created:
                        p.save()
                    if p not in i.pairs.all():
                        i.pairs.add(p)
                        i.save()
                    assert p in i.pairs.all()

    def extract_data_url(self, current_url, level):
        if "InstanceID" not in current_url:
            return None
        if current_url in exclude:
            return None
        if not current_url.startswith(self.prefix):
            print("[ERROR] %s %d" % (current_url, level))

        else:
            soup = BeautifulSoup(requests.get(current_url, auth=auth).content, features="html.parser")
            body = soup.find('body') if soup.find('body') else None
            if not body:
                return None
            table_info = body.find("table", {"id": "MeetingInfo"})
            if table_info:
                meeting_date = table_info.find("td", {"id": "MeetingDate"}).text
                i_begin = meeting_date.find("(")
                i_end = meeting_date.find(")", i_begin)
                dt = meeting_date[i_begin + 1:i_end].replace('\\u002f', '/').split(',')
                self.meeting_date_begin = get_datetime(dt[0], dt[1])
                self.meeting_date_end = get_datetime(dt[2], dt[3])
                self.instanceid = urlparse.parse_qs(urlparse.urlparse(current_url).query)['InstanceID'][0]
                self.slug = format(self.website.name + self.instanceid)
            if "The meeting occurrence you are trying to access does not exist within the Meeting Workspace" \
                    in soup.text:
                return None
            self.p_name = urlparse.parse_qs(urlparse.urlparse(current_url).query)['InstanceID'][0]
            page, created = Page.objects.get_or_create(name=self.p_name,
                                                       url=current_url,
                                                       slug=self.slug,
                                                       datetime_begin=self.meeting_date_begin,
                                                       datetime_end=self.meeting_date_end,
                                                       ref_website=self.website)
            if created:
                page.save()
            if page not in self.website.pages.all():
                self.website.pages.add(page)
                self.website.save()
            for collection in soup.findAll("div", {"class": "ms-webpart-chrome-title"}):
                col_id = str(collection.get('id').split('_')[0])
                title_id = col_id.replace('WebPartWPQ', 'WebPartTitleWPQ')
                if "WebPartTitleWPQ9" == title_id:
                    title = collection.text.replace(u'\xa0', ' ')
                    c_name = "%s - %s " % (page, title)
                else:
                    div_title = body.find("span", {"id": title_id})
                    try:
                        title = div_title.find('a').text.lstrip()
                    except:
                        title = "undefined"
                    c_name = "%s " % title
                    if "Meeting Documents" in c_name:
                        c_name = "Document Library"
                c, created = Collection.objects.get_or_create(name=c_name, ref_website=self.website, ref_page=page)
                if created:
                    c.save()
                if c not in page.collections.all():
                    page.collections.add(c)
                    page.save()
                if "Site Users" in title:
                    self.extract_site_users(c, body)
                elif "Document Library" in title:
                    self.extract_document_library(c)
                elif "Meeting Documents" in title:
                    self.extract_document_library(c)
                elif "Agenda" in title:
                    # je vais sur la page de l'agenda de la réunion
                    detail_url = self.prefix + "Lists/" + title + "/AllItems.aspx?InstanceID=" + self.instanceid
                    soup2 = BeautifulSoup(requests.get(detail_url, auth=auth).content, features="html.parser")
                    for i, tr in enumerate(soup2.find(
                            "div", {"id": "WebPartWPQ2"}).findAll(
                            "tr", {"class": "ms-itmhover"})):
                        i_name = "%s_%s_%s_%s " % (self.website, page.pk, c.pk, i+1)
                        i, created = Item.objects.get_or_create(name=i_name, ref_website=self.website, ref_collection=c)
                        if created:
                            i.save()
                        if i not in c.items.all():
                            c.items.add(i)
                            c.save()
                        assert i in c.items.all()
                        td = tr.find("td", {"class": "ms-vb-title"})
                        div = td.find("div", {"class": "ms-vb itx"})
                        item_id = div['id']
                        item_url = self.prefix + "Lists/Agenda/DispForm.aspx?ID=" + item_id
                        soup3 = BeautifulSoup(requests.get(item_url, auth=auth).content, features="html.parser")
                        begin = str(soup3).find("var WPQ2FormCtx =")
                        end = str(soup3)[begin+17:].find("};")
                        json_data = str(soup3)[begin + 17:begin + 18 + end]
                        dict_data = json.loads(json_data)
                        for key, value in dict_data['ListData'].items():
                            key, value = manage_key_value(key, value)
                            if 'Document' in key and value:
                                check = True
                                print(value)
                                for val in value.split(";#"):
                                    if check:
                                        document_url = self.prefix + "Document%20Library/Forms/DispForm.aspx?ID=" + val.replace(";", "")
                                        print(document_url)
                                        self.extract_document(document_url, i)
                                    check = not check
                            if key == "Attachments":
                                if 'UrlPrefix' in value:
                                    url_prefix = value['UrlPrefix']
                                if 'Attachments' in value:
                                    for attach in value['Attachments']:
                                        if attach['RedirectUrl']:
                                            redirect_url = attach['RedirectUrl']
                                            if 'sourcedoc' in redirect_url:
                                                ru = redirect_url.split('sourcedoc=')[1]
                                                ru = ru.split('&action')[0]
                                                url_sp = self.adjust_sp_url(ru)
                                                url_sp = unparse(url_sp)
                                        else:
                                            url_sp = url_prefix + attach['FileName']
                                        url = parse(url_sp)
                                        local_url = os.path.join("documents", self.website.name, self.p_name,
                                                                 url_sp.split('/')[-1])
                                        self.download_document(local_url, url)
                                        d, created = Document.objects.get_or_create(name=url_sp.split('/')[-1], url=url,
                                                                                    local_url=local_url,
                                                                                    ref_website=self.website,
                                                                                    ref_item=i)
                                        if created:
                                            d.save()
                                        if d not in i.documents.all():
                                            i.documents.add(d)
                                            i.save()
                                        assert d in i.documents.all()
                            else:
                                if key and value:
                                    p, created = Pair.objects.get_or_create(key=key, value=value)
                                    if created:
                                        p.save()
                                    if p not in i.pairs.all():
                                        i.pairs.add(p)
                                        i.save()
                                    assert p in i.pairs.all()
                else:
                    try:
                        for tr in body.find("div", {"id": col_id}).find("table").find("table").findAll("tr"):
                            if tr.find('a'):
                                new_url = None
                                if '/entities/' in tr.find('a')['href']:
                                    new_url = parse(
                                        tr.find('a')['href'].replace('/entities/',
                                                                     'https://collab-famhp.yourict.be/entities/'))
                                elif '/KC/' in tr.find('a')['href']:
                                    new_url = parse(
                                        tr.find('a')['href'].replace('/KC/',
                                                                     'https://collab-famhp.yourict.be/KC/'))
                                elif '/SPDEV/' in tr.find('a')['href']:
                                    new_url = parse(
                                        tr.find('a')['href'].replace('/SPDEV/',
                                                                     'https://collab-famhp.yourict.be/SPDEV/'))
                                if new_url:
                                    if "ID=" in new_url:
                                        item_id = urlparse.parse_qs(urlparse.urlparse(new_url).query)['ID'][0]
                                        detail_url = self.prefix + "Lists/" + title + "/DispForm.aspx?ID=" + item_id
                                        i_name = "%s " % item_id
                                        i, created = Item.objects.get_or_create(name=i_name, ref_website=self.website,
                                                                                ref_collection=c)
                                        if created:
                                            i.save()
                                        if i not in c.items.all():
                                            c.items.add(i)
                                            c.save()
                                        assert i in c.items.all()
                                        soup2 = BeautifulSoup(requests.get(detail_url, auth=auth).content,
                                                              features="html.parser")
                                        data = str(soup2)
                                        i_begin = data.find('"ListData')
                                        dict_data = json.loads(str(soup2)[i_begin + 11:data.find('}', i_begin) + 1])
                                        for key, value in dict_data.items():
                                            key, value = manage_key_value(key, value)
                                            if key:
                                                p, created = Pair.objects.get_or_create(key=key, value=value)
                                                if created:
                                                    p.save()
                                                if p not in i.pairs.all():
                                                    i.pairs.add(p)
                                                    i.save()
                                                assert p in i.pairs.all()
                    except:
                        print("no tables")


# @app.task
def run(pk):
    print("run")
    w = Website.objects.get(pk=pk)
    if w.running:
        return None
    w.running = True
    w.save()
    p = ParserHtml(w)
    p.run()
    w.running = False
    w.save()
    output = open("output.txt", "w")
    for p in Page.objects.all():
        output.write(" ============= PAGE %s =======================\n" % p)
        for c in p.collections.all():
            output.write(" ------------ Collection %s -------------\n" % c)
            for i in c.items.all():
                output.write("+++++++ %s ++++++++++++++++++++\n" % i)
                for d in i.documents.all():
                    output.write("[DOCUMENT] %s \n" % d)
                    # for key, value in d.__dict__.items():
                        # print("%s : %s" % (key, value))
                        # output.write("[DOCUMENT PAIR] %s : %s\n" % (key, re.escape(value)))
                    # print(". . . . . . . . . . . ")
                for p in i.pairs.all():
                    output.write("[PAIR] %s : %s\n" % (p.key, p.value))
    output.close()
    return True
