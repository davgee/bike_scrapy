# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
import json
from bike_data.items import BikeDataItem
from scrapy.exceptions import CloseSpider
from scrapy.http import Request

URL = 'https://olx.pl/sport-hobby/rowery/?page=%d'


class OlxBikeSpider(scrapy.Spider):
    name = 'olx_bike'
    allowed_domains = ['olx.com', 'olx.pl']
    start_urls = [URL % 1]

    def __init__(self):
        self.page_number = 1

    def start_requests(self):
        urls = [
            'https://olx.pl/sport-hobby/rowery/?page=%d'
        ]
        for i in range(1, 600):
            url_to_sc = urls[0] % i
            yield scrapy.Request(url=url_to_sc, callback=self.parse)

    def parse(self, response):
        OFFER_SELECTOR = "div.offer-wrapper"

        if self.page_number > 600:
            raise CloseSpider("No more jobs.")
        for offer in response.css(OFFER_SELECTOR):
            
            OFFER_URL_SELECTOR = "a::attr(href)"
            TITLE_AND_PRICE_SELECTOR = "strong::text"
            PLACE_AND_TIME_SELECTOR = "span::text"
            OFFER_ID_SELECTOR = "table::attr(data-id)"

            url_and_promoted = offer.css(OFFER_URL_SELECTOR).extract()
            title_and_price = offer.css(TITLE_AND_PRICE_SELECTOR).extract()
            place_and_time = offer.css(PLACE_AND_TIME_SELECTOR).extract() 
            offer_id = offer.css(OFFER_ID_SELECTOR).extract_first()

            offer_time = place_and_time[-4].replace("\n", "").replace("\t", "")    # Date is in array
            offer_place = (place_and_time[1].replace("\n", "").replace("\t", "") + ' ' 
                + place_and_time[2]).replace("\n", "").replace(" ", "").replace(",", ", ").replace("\t", "")
            offer_price = float(title_and_price[1].replace(" zł", "").replace(" ", "").replace(",", ".").replace("Zadarmo","0").replace("Zamienię", "0"))
            item = {
                'title': title_and_price[0],
                'price': offer_price,
                'url_addres': url_and_promoted[0],
                'add_time': self.translate_datetime(offer_time),
                'place': offer_place,
                'paid_offer': 'promoted' in url_and_promoted[1],
                'id': offer_id
            } 
            if item["url_addres"]:
                yield Request(
                    url=item["url_addres"], 
                    callback=self.parse_page2, 
                    meta={
                        'item': item, 
                        'dont_redirect': True,
                        'handle_httpstatus_list': [302]
                        }
                )
            else:
                yield BikeDataItem(
                    title=title_and_price[0], 
                    price=offer_price,
                    url_addres= url_and_promoted[0],
                    add_time= self.translate_datetime(offer_time),
                    place= offer_place,
                    paid_offer= 'promoted' in url_and_promoted[1],
                    id=offer_id,
                )
        self.page_number += 1
        yield Request(
            URL % self.page_number,
            meta={
                'dont_redirect': True,
                'handle_httpstatus_list': [302]
                }
        )
            
        self.log(f'Ended spider')


    def parse_page2(self, response):
        item = response.meta['item']
        ADDED_VIA_MOBILE = "i::attr(data-icon)"
        DESCRIPTION = "div.clr.lheight20.large"

        all_data_icons = response.css(ADDED_VIA_MOBILE).getall()
        offer_added_via_mobile = "mobile" in all_data_icons

        desc = response.css(DESCRIPTION).getall()
        # Theres some replacements to make it readable...
        a = "".join(desc).replace("\n", " ")
        b = a.replace("  ", " ")
        offer_description = b.replace("  ", " ")

        yield BikeDataItem(
            title=item['title'], 
            price=item['price'],
            url_addres= item['url_addres'],
            add_time= item['add_time'],
            place= item['place'],
            paid_offer=item['paid_offer'],
            id=item['id'],
            added_via_phone=offer_added_via_mobile,
            description=offer_description,
        )



    def translate_datetime(self, input):
        current_datetime = datetime.datetime.now()
        input_array = re.split(" |:", input)
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
