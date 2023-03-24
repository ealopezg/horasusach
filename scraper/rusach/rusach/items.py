# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags

class RusachItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class SchoolItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    programs = scrapy.Field()

class ProgramItem(scrapy.Item):
    id_program = scrapy.Field()
    id_school = scrapy.Field()
    name = scrapy.Field()
    period = scrapy.Field()
    schedule = scrapy.Field()