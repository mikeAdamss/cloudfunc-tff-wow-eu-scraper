try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    try:
        from beautifulsoup4 import BeautifulSoup
    except ImportError:
        from bs4 import BeautifulSoup

from discord_webhook import DiscordWebhook

import datetime
import requests
import yaml
import re
import os

import dateutil.parser

# NOTE - done in a rush, this is a bit of a mess!

def main(event, context):

    r = requests.get('https://eu.forums.blizzard.com/en/wow/c/recruitment/guild-recruitment/')

    soup = BeautifulSoup(r.content)
    links = soup.findAll('a', attrs={'href': re.compile("^https://eu.forums.blizzard.com/en/wow/t/")})

    links = [x["href"].split("/")[-2] for x in links]

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
            filtered_links.append("https://eu.forums.blizzard.com/en/wow/t/" + l)

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
                print("Found line:", line)
                choice = i
                break

        if choice == "":
            print("failed on", filtered_link)
        else:

            line = str(rfl.content).split("\\n")[choice]
            print(line)

            # For debugging
            print("1st timesplit is:", line.split("<time itemprop=\\'datePublished\\' datetime=\\'"))
            time_string = line.split("<time itemprop=\\'datePublished\\' datetime=\\'")[1].split("\\")[0]
            url_and_date_created.update({filtered_link: time_string})

    # now filter out anything more than an hour old
    hook = os.getenv("DISCORD_RECRUITMENT_WEBHOOK")
    for url, time_string in url_and_date_created.items():

        time_created = dateutil.parser.parse(time_string)
        time_created = time_created.replace(tzinfo=None)

        time_one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        time_one_hour_ago = time_one_hour_ago.replace(tzinfo=None)

        print(time_created, time_one_hour_ago)
        if time_created > time_one_hour_ago:
            webhook = DiscordWebhook(url=hook, content=url)
            webhook.execute()
            print(url)
