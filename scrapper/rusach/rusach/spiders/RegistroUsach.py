import scrapy


class RegistrousachSpider(scrapy.Spider):
    name = 'RegistroUsach'
    allowed_domains = ['registro.usach.cl']
    start_urls = [f'https://registro.usach.cl/index.php?ct=horario&mt=muestra_horario']

    def parse(self, response):
        pass
