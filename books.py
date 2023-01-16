import scrapy


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']

    def parse(self, response):
        books = response.xpath("//article[@class='product_pod']")
        for book in books:
            instock = ''.join(book.xpath(".//p[contains(@class, 'instock')]/text()").getall()).strip()
            yield {
                'image': response.urljoin(book.xpath(".//div[@class='image_container']/a/img/@src").get()),
                'title': book.xpath(".//h3/a/@title").get(),
                'price': book.xpath(".//p[@class='price_color']/text()").get(),
                'instock': instock
            }
        next_page = response.xpath("//li[@class='next']/a[contains(text(), 'next')]/@href").get()
        if next_page:
            next_page_link = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_link, callback=self.parse)