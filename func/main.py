
try:
    from requests_html import HTMLSession
except ImportError:
    from requests-html import HTMLSession
    
import datetime
import requests
import yaml

import dateutil.parser

# NOTE - done in a rush, this is a bit of a mess!

def main(event, context):

    session = HTMLSession()
    r = session.get('https://eu.forums.blizzard.com/en/wow/c/recruitment/guild-recruitment/')

    link_boiler_plate = "https://eu.forums.blizzard.com/en/wow/t/"

    links = r.html.absolute_links
    links = [x.split("/")[-2] for x in links if x.startswith(link_boiler_plate)]

    r = requests.get("https://raw.githubusercontent.com/mikeAdamss/cloudfunc-tff-wow-eu-scraper/master/rules.yaml")
    rules = yaml.load(r.content)

    filtered_links = []
    for l in links:

        keep = True
        for rule, args in rules.items():

            for arg in args:

                if rule == "link_should_not_contain":
                    if arg in l:
                        keep = False

                if rule == "link_should_not_begin_with":
                    if l.startswith(arg):
                        keep = False

                if rule == "link_should_not_end_with":
                    if l.endswith(arg):
                        keep = False

                if rule == "link_should_only_contain_key_with_value":
                    for k in arg.keys():
                        thing1 = k
                        thing2 = arg[k]

                    if thing1 in l and thing2 not in l:
                        keep = False

        if keep:
            filtered_links.append(link_boiler_plate + l)

    # go through and find the creation time for each url
    url_and_date_created = {}
    for filtered_link in filtered_links:

        rfl = requests.get(filtered_link)
        if rfl.status_code != 200:
            print("Scrape failed for {} with {}".format(filtered_link, r.status_code))

        choice = ""
        lines = str(rfl.content).split("\\n")
        for i, line in enumerate(lines):

            if "datePublished" in line:
                choice = i+1
                break

        if choice == "":
            print("failed on", filtered_link)
        else:

            time_string = line.split("<time datetime=\\'")[1].split("\\")[0]
            url_and_date_created.update({filtered_link: time_string})

    # now filter out anything more than an hour old
    for url, time_string in url_and_date_created.items():

        time_created = dateutil.parser.parse(time_string)
        time_created = time_created.replace(tzinfo=None)

        time_one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        time_one_hour_ago = time_one_hour_ago.replace(tzinfo=None)

        print(time_created, time_one_hour_ago)
        if time_created > time_one_hour_ago:
            print(url)
