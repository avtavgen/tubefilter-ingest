import requests
import sys
from time import sleep
from random import randint
from datetime import datetime
from bs4 import BeautifulSoup


class TubefilterProcessor(object):
    def __init__(self, entity, log, retry=3):
        self.log = log
        self.retry = retry
        self.entity = entity
        self.base_url = "https://tubefilter.com"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def _make_request(self, url):
        retries = 0
        while retries <= self.retry:
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                self.log.info("{}".format(e))
                sleep(30)
                break
            except Exception as e:
                self.log.info("{}: Failed to make request on try {}".format(e, retries))
                retries += 1
                if retries <= self.retry:
                    self.log.info("Trying again!")
                    continue
                else:
                    sys.exit("Max retries reached")

    def _get_users(self):
        self.info = []
        response = self._make_request(self.base_url + "/tag/Tubefilter-Charts/")
        soup = BeautifulSoup(response.content, "html.parser")
        wrapper = soup.find("div", class_="scb scb-4")
        groups = wrapper.find_all("div", class_="group")
        for group in groups:
            try:
                url = group.find("a", href=True)
                week = url.text.split(" • ")
                users_data = self._get_user_info(url["href"], week[1])
                for user_data in users_data:
                    self.info.append(user_data)
                sleep(randint(4, 10))
            except Exception as e:
                self.log.info("Failed to fetch creator: {}".format(e))
        self.entity.save(users=self.info)

    def _get_user_info(self, url, week):
        creators_list = []
        user_data = dict()
        today = datetime.now().strftime("%Y-%m-%d")
        response = self._make_request(url)
        soup = BeautifulSoup(response.content, "html.parser")
        chart = soup.find("div", id="ytChart")
        creators = chart.find_all("div", class_="channelRow")
        for creator in creators:
            this_week = creator.find("span", class_="channelSecondaryDetails").text.split("|")
            all_time = creator.find("span", class_="channelTertiaryDetails").text.split("|")
            fans_week = this_week[0].split("Fans This Week:")[1].strip()
            position_week = this_week[1].split("Position Last Week:")[1].strip()
            fans_all_time = all_time[0].split("All-Time Fans:")[1].strip()
            diamonds_all_time = all_time[1].split("All-Time Diamonds:")[1].strip()
            user_data["week"] = week
            user_data["name"] = creator.find("span", class_="channelName").find("a", href=True).text
            user_data["position_this_week"] = int(creator.find("div", class_="channelRank").text)
            try:
                user_data["fans_week"] = int(fans_week.replace(",", ""))
            except:
                user_data["fans_week"] = None
            try:
                user_data["position_last_week"] = int(position_week.replace(",", ""))
            except:
                user_data["position_last_week"] = None
            try:
                user_data["fans_all_time"] = int(fans_all_time.replace(",", ""))
            except:
                user_data["fans_all_time"] = None
            try:
                user_data["diamonds_all_time"] = int(diamonds_all_time.replace(",", ""))
            except:
                user_data["diamonds_all_time"] = None
            user_data["date"] = today
            creators_list.append(user_data)
            self.log.info(user_data)

        return creators_list

    def fetch(self):
        self.log.info('Making request to Socialblade for daily creators export')
        self._get_users()
        return self
