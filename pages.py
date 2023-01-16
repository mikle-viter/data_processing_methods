import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class PagesSpider(CrawlSpider):
    name = 'pages'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    rules = (
        Rule(LinkExtractor(restrict_xpaths=r"//li[@class='next']/a"), follow=True),
        Rule(LinkExtractor(restrict_xpaths="//article[@class='product_pod']/h3/a"), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {}
        row = response.xpath("//div[@class='row']")
        product_main = row.xpath(".//div[contains(@class,'product_main')]")
        item['title'] = product_main.xpath(".//h1/text()").get()
        item['price'] = product_main.xpath(".//p[@class='price_color']/text()").get()
        item['in_stock'] = ''.join(product_main.xpath(".//p[contains(@class, 'instock')]/text()").getall()).strip()
        item['product_description'] = ''.join(
            row.xpath("//div[@id='product_description']/following::p[1]/text()").getall()).strip()
        table = row.xpath("//div[@id='product_description']/following::table[contains(@class, 'table')]")
        item['upc'] = table.xpath("//th[contains(text(),'UPC')]/following::td[1]/text()").get()
        item['product_type'] = table.xpath("//th[contains(text(),'Product Type')]/following::td[1]/text()").get()
        item['price_excl_tax'] = table.xpath("//th[contains(text(),'Price (excl. tax)')]/following::td[1]/text()").get()
        item['price_incl_tax'] = table.xpath("//th[contains(text(),'Price (incl. tax)')]/following::td[1]/text()").get()
        item['tax'] = table.xpath("//th[contains(text(),'Tax')]/following::td[1]/text()").get()
        item['availability'] = table.xpath("//th[contains(text(),'Availability')]/following::td[1]/text()").get()
        item['number_of_reviews'] = table.xpath("//th[contains(text(),'Number of reviews')]/following::td[1]/text()").get()
        yield item
