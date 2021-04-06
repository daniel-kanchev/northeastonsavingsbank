import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from northeastonsavingsbank.items import Article
import requests
import json


class northeastonsavingsbankSpider(scrapy.Spider):
    name = 'northeastonsavingsbank'
    start_urls = ['https://www.northeastonsavingsbank.com/']

    def parse(self, response):

        json_response = json.loads(requests.get("https://www.northeastonsavingsbank.com/api/news_listing/?list=1000&page=1&category=Category+1").text)
        articles = json_response["pages"]
        for article in articles:
            link = response.urljoin(articles[article]['link'])
            date = articles[article]["date"]
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="col-12 col-md-6 col-lg-7 order-md-0"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
