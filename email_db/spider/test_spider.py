# -*- coding: utf-8 -*-
import scrapy
from email_db.items import EmailDbItem 

class TestSpiderSpider(scrapy.Spider):
    name = "test_spider"
    allowed_domains = ["www.baidu.com"]
    start_urls = ['http://www.baidu.com/']
    
    def __init__(self, a='/home/yyb/py_env/scrapy_email_code/email_db/email_data/reg_lower.csv', b=200000, *args, **kwargs):
        super(TestSpiderSpider, self).__init__(*args, **kwargs)
        print a
	print b

    def parse(self,response):
        a = EmailDbItem()
	return a
