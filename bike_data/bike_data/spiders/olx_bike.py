# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
from bike_data.items import BikeDataItem
from bike_data.database_utils import DBHelper
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.selector import Selector


def check_if_promoted(value):
    check = 'promoted' in value[1]
    return check

def price_in_fun(value):
    a = value[1].replace(" zł", "").replace(" ", "").replace(",", ".").replace("Zadarmo","0").replace("Zamienię", "0")
    return a

def time_and_place_in_fun(value):
    value = [x for x in value if x != "Do negocjacji"]
    return value

def second_arg(value):
    if value[0] == "Brak zdjęcia":
        a = value[2].replace("  ", " ")
    else:
        a = value[1].replace("  ", " ")
    a = translate_datetime(a)
    return a

def added_via_phone_in(value):
    if len(value) > 0:
        return [True]
    else:
        return [False]

class BikeLoader(ItemLoader):
    url_addres_out = TakeFirst()
    paid_offer_out = check_if_promoted
    title_out = TakeFirst()

    price_in = price_in_fun
    price_out = TakeFirst()

    add_time_in = time_and_place_in_fun
    add_time_out = second_arg

    place_in = time_and_place_in_fun
    place_out = TakeFirst()

    id_out = TakeFirst()

    added_via_phone_in = added_via_phone_in


class RunController:
    __instance = None
    continue_scrapping = True

    @staticmethod
    def get_instance():
        if RunController.__instance is None:
            RunController()
        return RunController.__instance

    def dont_continue(self):
        self.continue_scrapping = False

    def check_if_continue(self):
        return self.continue_scrapping

    def __init__(self):
        if RunController.__instance is not None:
            raise Exception("This class is singleton instance!")
        else:
            RunController.__instance == self

rc = RunController()

class OlxBikeSpider(scrapy.Spider):
    name = 'olx_bike'
    allowed_domains = ['olx.com', 'olx.pl']
    headers = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-User': '?1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

    def __init__(self):
        self.page_number = 1


    def start_requests(self):
        urls = [
            'https://www.olx.pl/sport-hobby/rowery/?page=%d'
        ]
        for i in range(1, 100):
            url_to_sc = urls[0] % i
            if rc.check_if_continue():
                yield scrapy.Request(url=url_to_sc, callback=self.parse, headers=self.headers)
            else:
                self.log(f"Breaking!")
                break

    def parse(self, response):

        OFFER_SELECTOR = "div.offer-wrapper"
        # TODO : zzrobić koniec gdy osiągniemy datę

        finish_flag = False
        latest_offer_time = DBHelper().get_last_offer_time()
        self.log(f'Starting Job - parsing function. Latest offer time is {latest_offer_time}. Run Controller = {rc}')
        for offer in response.css(OFFER_SELECTOR):
            item_loader = BikeLoader(item=BikeDataItem(), response=response, selector=offer)
            OFFER_URL_SELECTOR = "a::attr(href)"
            TITLE_AND_PRICE_SELECTOR = "strong::text"
            PLACE_AND_TIME_SELECTOR = "span::text"
            OFFER_ID_SELECTOR = "table::attr(data-id)"
            item_loader.add_css('title', TITLE_AND_PRICE_SELECTOR)
            item_loader.add_css('price', TITLE_AND_PRICE_SELECTOR)
            item_loader.add_css('url_addres', OFFER_URL_SELECTOR)
            item_loader.add_css('add_time', PLACE_AND_TIME_SELECTOR)
            item_loader.add_css('place', PLACE_AND_TIME_SELECTOR)
            item_loader.add_css('paid_offer', OFFER_URL_SELECTOR)
            item_loader.add_css('id', OFFER_ID_SELECTOR)
            it = item_loader.load_item()

            item_date = datetime.datetime.strptime(it['add_time'], "%Y-%m-%d %H:%M:%S")
            if item_date < latest_offer_time and not it['paid_offer']:
                self.log(f"Setting finish flag to True. Item paid = {it['paid_offer']}, "
                         f"Item time add = {it['add_time']}, latest offer in db = {latest_offer_time}")
                rc.dont_continue()
                return
            if not finish_flag:
                self.log(f"Requesting new page - with details for {it['title']}")
                yield Request(
                    url=it["url_addres"],
                    callback=self.parse_page2,
                    meta={
                        'item': it,
                        'dont_redirect': True,
                        'handle_httpstatus_list': [302]
                    },
                    headers=self.headers
                )
            else:
                self.log(f'Ended spider by reaching latest time.')
                yield None


    def parse_page2(self, response):
        item = response.meta['item']
        ADDED_VIA_MOBILE = "div.addedbymobile::text"
        DESCRIPTION = "div.clr.lheight20.large"

        all_data_icons = response.css(ADDED_VIA_MOBILE)
        offer_added_via_mobile = len(all_data_icons) > 0
        # TODO : Dodać kategorię ogłoszenia
        desc = response.css(DESCRIPTION).xpath('//div[@class = "clr lheight20 large"]/text()').getall()
        desc = " ".join(desc)
        desc = desc.replace("  ", "")
        # Theres some replacements to make it readable...
        a = "".join(desc).replace("\n", " ")
        b = a.replace("  ", " ")
        offer_description = b.replace("  ", " ")
        category = response.xpath('//a[@class="link nowrap"]/span')[-1].extract().replace('<span>', '').replace('</span>', '')
        item['added_via_phone'] = offer_added_via_mobile
        item['description'] = offer_description
        item['category'] = category

        if 'Akcesoria' in item['category']:
            return None
        else:
            yield item


def translate_datetime(input):
    current_datetime = datetime.datetime.now()
    input_array = re.split(" |:", input)
    print("Wrong input", input_array)
    if ((len(input_array) > 1) and (str(input_array[1]) != '')):
        if input_array[0] == "wczoraj":
            current_datetime = current_datetime.replace(day=current_datetime.day-1)
            current_datetime = current_datetime.replace(hour=int(input_array[1]), minute=int(input_array[2]), second=00)
        elif input_array[0] == "dzisiaj":
            current_datetime = current_datetime.replace(day=current_datetime.day)
            current_datetime = current_datetime.replace(hour=int(input_array[1]), minute=int(input_array[2]), second=00)
        else:
            current_datetime = current_datetime.replace(hour=00, minute=00, second=00)
    else:
        # TODO zrobić handling dla wcześniejszych dat
        lista_mies = ['sty', 'lut', 'mar', 'kwi', 'maj', 'cze', 'lip', 'sie', 'wrz', 'paź', 'lis', 'gru']
        offer_month = lista_mies.index(input_array[2])+1
        print(input_array)
        current_datetime = current_datetime.replace(month=offer_month, day=int(input_array[0]), hour=00, minute=00, second=00)
        print(str(current_datetime))
    formatted = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted
