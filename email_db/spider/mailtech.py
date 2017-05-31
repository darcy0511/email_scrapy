# -*- coding: utf-8 -*-
import scrapy
import random
from scrapy.selector import Selector
from email_db.items import EmailDbItem 

class MailtechSpider(scrapy.Spider):
    name = "mailtech"
    allowed_domains = ["mailtech.cn"]
    start_urls = ['http://mail.mailtech.cn/ym/']
    url_search = 'http://mail.mailtech.cn/ym/mail/Domains'
    
    def __init__(self, filepath='/home/yyb/py_env/scrapy_email_code/email_db/email_data/reg_lower.csv', minloc='0', maxloc='0', *args, **kwargs):
	super(MailtechSpider, self).__init__(*args, **kwargs)
	self.filepath = filepath
	self.maxloc = int(maxloc)
	self.minloc = int(minloc)

    def parse(self, response):
        with open(self.filepath, 'rU') as f:
            for num,line in enumerate(f):
	        if num >= self.minloc and num <= self.maxloc:
                    line = line.replace(' ','')
		    if line.find('.') == -1:
                        continue
		
		    postStr = """domain:{}
		                 id:{} 
                                 tran:1
		                 address:undefined
			         tj:1
			         size:1""".format(line,random.randint(1,10**28))
		    postData = {x.strip().split(":")[0]:x.split(":")[1] for x in postStr.split("\n") if x}
		    self.logger.info('Parse function called on %s', line)
		    yield scrapy.http.FormRequest(self.url_search, formdata=postData, meta={"NUM":num} ,callback=self.parse_mailtech)

    def parse_mailtech(self, response):
	item = EmailDbItem()
	item['NUM'] = response.meta["NUM"]
	print response.meta
        item['DNS'] = Selector(response=response).xpath('//dns/text()').extract()[0].encode('utf8')
	#self.logger.info('Item function called on %s', Selector(response=response).xpath('//dns/text()').extract())
	item['MX'] = Selector(response=response).xpath('//mx/text()').extract()[0].encode('utf8')
	#self.logger.info('Item function called on %s', Selector(response=response).xpath('//mx/text()').extract())
	item['SHORTNAME'] = Selector(response=response).xpath('//shortname/text()').extract()[0].encode('utf8')
	#self.logger.info('Item function called on %s', item['SHORTNAME']) 
	item['INFO'] = Selector(response=response).xpath('//info/text()').extract()[0].encode('utf8')
	#self.logger.info('Item function called on %s', item['INFO'])
	return item 
