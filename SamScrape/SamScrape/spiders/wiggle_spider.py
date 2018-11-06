import scrapy


class WiggleSpider(scrapy.Spider):
    name = "wiggle"

    custom_settings = {
        'LOG_ENABLED':True,
        'CONCURRENT_ITEMS':200,
        'CONCURRENT_REQUESTS':200,
        'CONCURRENT_REQUESTS_PER_DOMAIN':200
    }

    start_urls = [
        'http://www.wiggle.com/cycle/bikes/',
        'http://www.wiggle.com/cycle/bikes/?g=73'
        'http://www.wiggle.com/cycle/bikes/?g=145',
        'http://www.wiggle.com/cycle/bikes/?g=241'
    ]

    

        
    def parse(self, response):
        # follow links into each bike's page
        for href in response.css("div[class=bem-product-thumb--grid] a::attr(href)"):
            yield response.follow(href, self.parse_bike)

        # After we have parsed a whole page of bikes move onto the next (scrapy automatically ignores duplicate links)
        next_page = response.xpath('//a[./text()=">"]/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

           
    # Parses information from one bike on its own specific product page
    def parse_bike(self, response):

        # Define functions which can extract queries and handle exceptions

        def get_delivery(query):
            try:
                return response.css(query).extract_first().strip()
            except:
                return "No delivery information"


        def get_feature1(query):
            try:
                return response.css(query).extract_first().strip()
            except:
                return "No Feature 1"

        def get_feature2(query):
            try:
                return response.css(query).extract()[1].strip()
            except:
                return "No Feature 2"


        def get_discount(query):

            try:
                return response.css(query).extract_first().strip()
            except:
                return "No discount applied"


        def get_colour(query):
            try:
                return response.css(query)[1].extract().strip()
            except:
                if response.css(query)[0].extract().strip()[6:] == ' a color:':
                    return 'Choice of colours'
                else:
                    return response.css(query)[0].extract().strip()[6:]


        yield {
            'Product':response.css("h1::text").extract_first().strip(),
            'Price':response.xpath('//p[@class="bem-pricing__product-price js-unit-price"]/text()').extract_first().strip(),
            'Discount':get_discount("span[class=bem-pricing__list-price--saving]::text"),
            'Feature 1':get_feature1("li[class=bem-pdp__features-item]::text"),
            'Feature 2':get_feature2("li[class=bem-pdp__features-item]::text"),
            'Delivery method':get_delivery("li[class=qa-shipping-option] strong::text"),
            'Colour':get_colour("label[class=bem-sku-selector__option-label]::text")
        }

  