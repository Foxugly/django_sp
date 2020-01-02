# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
# from jinja2 import Environment, FileSystemLoader
import os
# from ..celery import app
from .models import Website
from page.models import Page, Collection, Item, Pair
import tempfile
import urllib.parse as urlparse
import unidecode
import requests
from requests_ntlm import HttpNtlmAuth
import getpass
import json

debug = False

PASSWORD = getpass.getpass()
USERNAME = "YOURICT\\RDV"
auth = HttpNtlmAuth(USERNAME, PASSWORD)


def format(s):
    return unidecode.unidecode(s).replace(" ", "_")


def parse(current_url):
    list_replace = [('é', '%c3%a9'), (' ', '%20')]
    for old, new in list_replace:
        current_url = current_url.replace(old, new)
    return current_url


class ParserHtml:
    url = None
    folder = 'website'
    max_level = 5
    list_visited_url = []
    list_url = []

    def __init__(self, w, folder=None, max_level=None):
        self.website = w
        self.name = w.name
        self.url = w.url
        self.prefix = w.prefix
        self.folder = folder if folder else self.name
        if max_level:
            self.max_level = max_level
        self.webdriver = webdriver.Chrome()
        # path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        # self.env = Environment(loader=FileSystemLoader(path))

    def run(self):
        self.extract_data_url(self.url, 0)
        self.webdriver.quit()

    def get_slug(self, current_url):
        return urlparse.parse_qs(urlparse.urlparse(current_url).query)['InstanceID'][0]

    def copy_doc(self, doc, meeting):
        print("DOWNLOAD : %s" % doc.url)
        root_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(root_directory)
        website_path = os.path.join(root_directory, "documents", format(self.name))
        meeting_path = os.path.join(website_path, format(meeting.slug))
        doc_path = os.path.join(meeting_path, format(doc.url.split('/')[-1]))
        relative_doc_path = os.path.join("documents", format(self.name), format(meeting.slug),
                                         format(doc.url.split('/')[-1]))
        if not os.path.exists(website_path):
            try:
                os.mkdir(website_path)
            except OSError:
                print("Creation of the directory %s failed" % website_path)
            else:
                print("Successfully created the directory %s " % website_path)
        if not os.path.exists(meeting_path):
            try:
                os.mkdir(meeting_path)
            except OSError:
                print("Creation of the directory %s failed" % meeting_path)
            else:
                print("Successfully created the directory %s " % meeting_path)
        print("DONWLOAD [%s] : %s -> %s" % (doc.name, doc.url, doc_path))
        r = requests.get(doc.url, auth=auth)
        with open(doc_path, 'wb') as f:
            f.write(r.content)
        print(relative_doc_path)
        doc.path = relative_doc_path
        doc.save()

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

    def extract_data_url(self, current_url, level):
        if debug:
            print(current_url)
        # template = self.env.get_template('meeting.html')
        list_meetings = []
        list_objectives = []
        list_attendees = []
        list_agenda = []
        list_documents = []
        meeting_subject = "subject"
        meeting_date = "date"
        if current_url.startswith(self.prefix):
            print("[OK] %s %d" % (current_url, level))
        else:
            print("[ERROR] %s %d" % (current_url, level))
        if level < self.max_level and current_url.startswith(self.prefix):
            html = requests.get(current_url, auth=auth)
            soup = BeautifulSoup(html.content, features="html.parser")
            body = soup.find('body')
            table_info = body.find("table", {"id": "MeetingInfo"})
            name = "undefined%s" % tempfile.NamedTemporaryFile().name
            if table_info:
                subject_raw = table_info.find("td", {"id": "MeetingTitle"}).text
                meeting_subject = subject_raw.replace('é', '&eacute;') if subject_raw else None
                meeting_date = table_info.find("td", {"id": "MeetingDate"}).text.split(';')[1].split(')')[0] + ")"
                meeting_date = meeting_date.replace('\u200e', '')
                name = '%s %s' % (table_info.find("td", {"id": "MeetingTitle"}).text, meeting_date)
            print("CREATE PAGE")
            print("name : %s" % name)
            print("url : %s" % self.url)
            print("slug : %s" % self.get_slug(self.url))
            page, created = Page.objects.get_or_create(name=name, url=self.url, slug=self.get_slug(self.url), body=body)
            if created:
                self.website.pages.add(page)
                self.website.save()
            list = soup.findAll("div", {"class": "ms-webpart-chrome-title"})
            for collection in list:
                col_id = str(collection.get('id').split('_')[0])
                title_id = col_id.replace('WebPartWPQ', 'WebPartTitleWPQ')
                div_title = body.find("span", {"id": title_id})
                title = div_title.find('a').text.lstrip()
                print(title)
                c, created = Collection.objects.get_or_create(name="%s - %s " % (page, title))
                if created:
                    page.collections.add(c)
                    page.save()
                for tr in body.find("div", {"id": col_id}).find("table").find("table").findAll("tr"):
                    if tr.find('a'):
                        if 'entities' in tr.find('a')['href']:
                            new_url = parse(
                                tr.find('a')['href'].replace('/entities/', 'https://collab-famhp.yourict.be/entities/'))
                            print(new_url)
                            if "ID=" in new_url:
                                item_id = urlparse.parse_qs(urlparse.urlparse(new_url).query)['ID'][0]
                                print(tr.find('a').text)
                                print(item_id)
                                detail_url = self.prefix + "Lists/" + title + "/DispForm.aspx?ID=" + item_id
                                print(detail_url)
                                i, created = Item.objects.get_or_create(name="%s - %d " % (c, item_id))
                                if created:
                                    c.items.add(i)
                                    c.save()
                                soup2 = BeautifulSoup(requests.get(detail_url, auth=auth).content,
                                                      features="html.parser")
                                data = str(soup2)
                                i_begin = data.find('"ListData')
                                dict_data = json.loads(str(soup2)[i_begin + 11:data.find('}', i_begin) + 1])
                                for key, value in dict_data.items():
                                    print("%s : %s " % (key, value))
                                    p, created = Pair.objects.get_or_create(key=key, value=value)
                                    if created:
                                        i.pairs.add(p)
                                        i.save()
            # c, created = Collection.objects.get_or_create(name="%s - MESSAGES" % page)
            # if created:
            #     page.collections.add(c)
            # messages = soup.find("div", {"id": "WebPartWPQ9999"})  # TODO
            # if messages:
            #     for idx, tbody in enumerate(messages.findAll("table")[0].findAll("table")[0].findAll("tbody")[0]):
            #
            #         if idx > 0:
            #             data_messages = tbody.findAll("td")
            #             if len(data_messages) > 1:
            #                 if debug:
            #                     print(data_messages[1].findAll("a")[0].text)
            #                 i, created = Item.objects.get_or_create(name="%s - MESSAGES" % c) # TODO continue
            #                 list_objectives.append(data_messages[1].findAll("a")[0].text)
            #                 m, created = Collection.objects.get_or_create(name="%s - %s" % (m, data_messages[1].findAll("a")[0].text))
            #                 m.save()
            #                 page.collections.add(m)
            # if debug:
            #     print("|======= MESSAGES ========|")
            #     print("======= OBJECTIVES ========")
            # try:
            #     objectives = soup.find("div", {"id": "WebPartWPQ5"})
            #     if objectives:
            #         first_table = objectives.findAll("table")
            #         if len(first_table):
            #             if first_table[0].findAll("table"):
            #                 for idx, tbody in enumerate(first_table[0].findAll("table")[0].findAll("tbody")[0]):
            #                     if idx > 0:
            #                         data_objectives = tbody.findAll("td")
            #                         if len(data_objectives) > 1:
            #                             if debug:
            #                                 print(data_objectives[1].findAll("a")[0].text)
            #                             list_objectives.append(data_objectives[1].findAll("a")[0].text)
            #                             o, created = Objective.objects.get_or_create(name=data_objectives[1].findAll("a")[0].text)
            #                             o.save()
            #                             meeting.objectives.add(o)
            # except:
            #     print("ERROR OBJECTIVES : %s" % meeting.name)
            # if debug:
            #     print("|======= OBJECTIVES ========|")
            #     print("======= ATTENDEES ========")
            # try:
            #     attendees = soup.find("div", {"id": "WebPartWPQ8"})
            #     if attendees:
            #         first_table = attendees.findAll("table")[0]
            #         if first_table.findAll("table"):
            #             for idx, tbody in enumerate(first_table.findAll("table")[0].findAll("tbody")[0]):
            #                 if idx > 0:
            #                     user, edit, attendance, response, comment = tbody.findAll("td")
            #                     user_data = [user.findAll('a')[0].text, edit.text, attendance.text, response.text,
            #                                  comment.text]
            #                     attendance, created = Attendance.objects.get_or_create(name=attendance.text)
            #                     user, created = CustomUser.objects.get_or_create(username=user.findAll('a')[0].text)
            #                     username = "%s (%s)" % (user.username, attendance.name)
            #                     attendee, created = Attendee.objects.get_or_create(name=username, user=user,
            #                                                                        attendance=attendance,
            #                                                                        response=response.text,
            #                                                                        comment=comment.text)
            #                     attendee.save()
            #                     meeting.attendees.add(attendee)
            #
            #                     if debug:
            #                         print(user_data)
            #                     list_attendees.append(user_data)
            # except:
            #     print("ERROR ATTENDEES : %s" % meeting.name)
            # if debug:
            #     print("|======= ATTENDEES ========|")
            #     print("======= AGENDA ========")
            # try:
            #     agenda = soup.find("div", {"id": "WebPartWPQ6"})   # TODO
            #     first_table = agenda.findAll("table")[0]
            #     if first_table.findAll("table"):
            #         for idx, tbody in enumerate(first_table.findAll("table")[0].findAll("tbody")[0]):
            #             data = tbody.findAll("td")
            #             if len(data) >= 7:
            #                 a_doc = data[2].findAll('a', href=True, )[0]
            #                 owner, created = CustomUser.objects.get_or_create(username=data[4].text)
            #                 agenda, created = Document.objects.get_or_create(name=a_doc.text, owner=owner)
            #                 meeting.agenda.add(agenda)
            # except:
            #     print("ERROR AGENDA : %s" % meeting.name)
            # if debug:
            #     print("|======= AGENDA ========|")
            #     print("======= DOCUMENTS ========")
            #
            # try:
            #     documents = soup.find("div", {"id": "WebPartWPQ7"})
            #     if documents:
            #         tables = documents.findAll("table")
            #         if len(tables) >= 3:
            #             first_table = tables[2]
            #             if first_table:
            #                 tbody = first_table.findAll("tbody")
            #                 if tbody:
            #                     data = tbody[0].findAll("td")
            #                     if len(data) >= 7:
            #                         # print(data)
            #                         a_doc = data[2].findAll('a', href=True, )[0]
            #                         button = data[3].findAll('a')[0]
            #                         document_data = [a_doc.text, a_doc['href'], data[4].text,
            #                                          data[6].findAll('span')[0]['title']]
            #                         owner, created = CustomUser.objects.get_or_create(username=data[4].text)
            #                         url = ""
            #                         if a_doc['href'].startswith('/entities/'):
            #                             new_url = a_doc['href'].replace('/entities/', 'https://collab-famhp.yourict.be/entities/')
            #                             url = parse(new_url)
            #                         document, created = Document.objects.get_or_create(name=a_doc.text, url=url,
            #                                                                            owner=owner,
            #                                                                            datetime=data[6].findAll('span')[0]['title'])
            #                         if created:
            #                             self.copy_doc(document, meeting])
            #                         meeting.documents.add(document)
            #                         if debug:
            #                             print(document_data)
            #                         list_documents.append(document_data)
            # except:
            #     print("ERROR DOCUMENTS : %s" % meeting.name)
            # if debug:
            #     print("|======= DOCUMENTS ========|")

            for anchor in soup.findAll('a', href=True, ):
                link = self.get_links(anchor)
                if link:
                    if link.startswith('http'):
                        if link not in self.list_visited_url:
                            if link not in self.list_url:
                                self.list_url.append(link)
                                self.extract_data_url(link, level + 1)
                                self.list_url.remove(link)
                                self.list_visited_url.append(link)
            #output = template.render(meeting_subject=meeting_subject, meeting_date=meeting_date,
            #                         list_meetings=list_meetings, list_objectives=list_objectives,
            #                         list_attendees=list_attendees, list_agenda=list_agenda,
            #                         list_documents=list_documents)
            #path_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            #f_out = open(os.path.join(path_out, 'example.html'), 'w')
            #f_out.write(output)
            #f_out.close()


# @app.task
def run(pk):
    w = Website.objects.get(pk=pk)
    if w.running:
        return None
    w.running = True
    w.save()
    print("BEGIN")
    p = ParserHtml(w, 'website', 50)
    p.run()
    print("END")
    w.running = False
    w.save()
    return True

# name : réunion_infra-dev_2017
# url : https://collab-famhp.yourict.be/entities/Soutien/ICTDivision/meetings/r%C3%A9union%20infra-dev%202017/default.aspx?InstanceID=20170808&Paged=Next&p_StartTimeUTC=20170808T090000Z&View=%7bA3BBE46D-F285-4A01-9255-FFF06E5951A1%7d
# prefix : https://collab-famhp.yourict.be/entities/Soutien/ICTDivision/meetings/r%C3%A9union%20infra-dev%202017/