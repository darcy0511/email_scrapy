# -*- coding: utf-8 -*-
import scrapy
from email_db.items import ChinazKeyDbItem

class ChinazKeySpider(scrapy.Spider):
    name = "chinaz_key"
    allowed_domains = ["whois.chinaz.com"]
    start_urls = ['http://whois.chinaz.com/']

    def __init__(self, filepath='/home/yyb/py_env/scrapy_email_code/email_db/email_data/reg_lower.csv', minloc='0', maxloc='0', *args, **kwargs):
        super(ChinazKeySpider, self).__init__(*args, **kwargs)
        self.filepath = filepath
        self.maxloc = int(maxloc)
        self.minloc = int(minloc)

    def parse(self, response):
        with open(self.filepath,'rU') as f:
            for num, line in enumerate(f):
                if num >= self.minloc and num <= self.maxloc:
                    line = line.replace(' ','').replace("\n","")
                    if line.find('.') == -1:
                        continue

                    #self.logger.info('Parse function called on {domain} of {num}'.format(domain=item['DOMAIN'],num=item["NUM"]))
                    url_search = "http://whois.chinaz.com/{domain}".format(domain=line)
                    yield scrapy.Request(url_search, meta={"num":num,'domain':line} ,callback=self.parse_whoischinaz)

    def parse_whoischinaz(self, response):
        num = response.meta['num']
        domain = response.meta['domain']
        return scrapy.http.FormRequest("http://whois.chinaz.com/getTitleInfo.ashx",formdata={"host":domain,"isupdate":"0"},meta={"num":num,'domain':domain},callback=self.parse_key)

    def parse_key(self,response):
        selector = scrapy.Selector(response=response)

        td_list = selector.xpath('//p/text()').extract()
        kk_list = selector.xpath('//p[@class="keyci"]/a/text()').extract()

        if len(td_list) == 0:
            return
        elif len(td_list) == 1:
            KEY_Title = td_list[0].encode("utf8")
            KEY_Description = ""
            KEY_KeyWords = ",".join(kk_list).encode("utf8")
        elif len(td_list) == 2:
            KEY_Title = td_list[0].encode("utf8")
            KEY_Description = td_list[1].encode("utf8")
            KEY_KeyWords = ",".join(kk_list).encode("utf8")
        else:
            raise IndexError
       
        item = ChinazKeyDbItem()
        item["NUM"] = response.meta['num']
        item["DOMAIN"] = response.meta['domain']
        item['KEY_Title'] = KEY_Title
        item['KEY_Description'] = KEY_Description
        item['KEY_KeyWords'] = KEY_KeyWords
        return item 


