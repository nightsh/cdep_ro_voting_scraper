# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".

from lxml import html
from datetime import timedelta, date
import re
# import sqlite3
import csv

# conn = sqlite3.connect('data.sqlite')
# c = conn.cursor
# print(c)
# c.execute("""drop table if exists data""")
# c.execute("""drop table if exists votes""")
# conn.commit()
# c.execute("""create table data (
#         date    int     primary key not NULL,
#         time    text,
#         vote    int,
#         description text,
#         presents    int,
#         yes         int,
#         no          int,
#         abstention  int,
#         no_vote     int)""")
# c.execute("""create table votes (
#         id    int     primary key not NULL,
#         name    text,
#         group   text,
#         vote    text)""")
# conn.commit()

min_date = date(2016, 12, 11)
max_date = date(2017, 9, 16)

ids = []
base_url = "http://www.cdep.ro/pls/steno/eVot"

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_date_summary(rows, formatted_date):
    with open('summary.csv', 'a') as f:
        writer = csv.writer(f)
        description_fragment = ""
        for row in rows[2:]:
            out = [formatted_date]
            cells = row.xpath("td")
            if len(cells[0].text_content()) > 1:
                for td in cells:
                    txt = td.text_content().replace("\n", " ").replace("\s+", " ").strip()
                    out.append(txt)
                    a = td.xpath("a")
                    if a:
                        link = a[0].attrib['href']
                        pattern = re.compile("^.*evot\.nominal\?idv=.*$")
                        if pattern.match(link):
                            ids.append((re.search("evot\.nominal\?idv=(.*)\&idl=2", link).group(1)))
                # c.execute("insert into data values ({}, {}, {}, {}, {}, {}, {}, {}, {})").format(
                # formatted_date,
                # *out
                # )
                # c.commit()
                if len(description_fragment) > 0:
                    out[3] = "{}. {}".format(description_fragment, out[3])
                description_fragment = ""
                print(out)
                writer.writerow(out)
            else:
                if len(cells) > 1:
                    description_fragment = cells[1].text_content()

def get_voting_summary(rows, id):
    with open('votes.csv', 'a') as f:
        writer = csv.writer(f)
        for row in rows[1:]:
            out = [id]
            cells = row.xpath("td")
            for td in cells:
                txt = td.text_content().replace("\n", " ").replace("\s+", " ").strip()
                out.append(txt)
            # print(out)
            # c.execute("insert into votes values ({}, {}, {}, {})").format(
            # id,
            # *out
            # )
            # c.commit()
            print(out)
            writer.writerow(out)

def get_summaries():
        for single_date in daterange(min_date, max_date):
            formatted_date = single_date.strftime("%Y%m%d")
            target = "{}.Data?dat={}&cam=2&idl=2".format(base_url, formatted_date)

            doc = html.parse(target)
            rows = doc.xpath("//*[@id='pageContent']/table/tr")
            if len(rows) > 2:
                print("Found {}".format(formatted_date))
                get_date_summary(rows, formatted_date)

def get_votes(ids):
    for id in ids:
        target = "{}.nominal?idv={}&idl=2".format(base_url, id)
        doc = html.parse(target)
        rows = doc.xpath("//body/table//table")[14].xpath("tr")
        # print(rows[0].xpath("td")[1].text_content())
        if len(rows) < 2:
            print("Shit happened, less than two rows")
        else:
            get_voting_summary(rows, id)


print("Gettings summaries")
get_summaries()

print("Gettings votes")
get_votes(ids)

# c.close()
