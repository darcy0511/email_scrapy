# -*- coding: utf-8 -*-
import scrapy
from email_db.items import ChinazDbItem
import traceback

class ChinazSpider(scrapy.Spider):
    name = "chinaz"
    #allowed_domains = ["http://chinaz.com"]
    start_urls = ['http://icp.chinaz.com/']
    
    def __init__(self, filepath='/home/yyb/py_env/scrapy_email_code/email_db/email_data/reg_lower.csv', minloc='0', maxloc='0', *args, **kwargs):
        super(ChinazSpider, self).__init__(*args, **kwargs)
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
				    
                    item = ChinazDbItem()
                    item['NUM'] = num
                    item['DOMAIN'] = line   
                    self.logger.info('Parse function called on {domain} of {num}'.format(domain=item['DOMAIN'],num=item["NUM"]))
                    url_search = 'http://icp.chinaz.com/?s={domain}'.format(domain=line)
                    yield scrapy.Request(url_search, meta={"item":item} ,callback=self.parse_icpchinaz)

    def parse_icpchinaz(self, response):
        selector = scrapy.Selector(response=response)
        item = response.meta['item']
        
        sp_list = selector.xpath('//li[@class="bg-gray clearfix"]/p/text()').extract()
        sn_list = selector.xpath('//strong[@class="fl fwnone"]/text()').extract()
        st_list = selector.xpath('//li[@class="clearfix"]/p/text()').extract()
        try:
            item['SPONSOR'] = sp_list[0].encode('utf8')
            item['SPONSOR_NATURE'] = sn_list[0].encode('utf8')
            item['DOMAIN_NAME'] = st_list[0].encode('utf8')
            item['SPONSOR_TIME'] = st_list[1].encode('utf8')
        except Exception,e:
            self.logger.warning(e)
	    traceback.print_exc()
        finally:
            url_search = "http://whois.chinaz.com/{domain}".format(domain=item['DOMAIN'])
            self.logger.info('Parse_ICP function called on {domain} of {num}'.format(domain=item['DOMAIN'],num=item["NUM"]))
	    return scrapy.Request(url_search,meta={"item":item,"flag":0},callback=self.parse_whoischinaz)

    def parse_whoischinaz(self, response):
        selector = scrapy.Selector(response=response)
        item = response.meta['item']
        flag = response.meta['flag']
	if flag == 4:
	    self.logger.info('Parse_WHOIS function called on {domain} of {num}'.format(domain=item['DOMAIN'],num=item["NUM"]))
	    return scrapy.http.FormRequest("http://whois.chinaz.com/getTitleInfo.ashx",formdata={"host":item["DOMAIN"],"isupdate":"1"},meta={"item":item},callback=self.parse_key) 
	if "Registrar_WHOIS_Server" in item:
	    url_search = "http://whois.chinaz.com/?Domain={domain}&isforceupdate=1&ws={whoisServer}".format(domain=item["DOMAIN"],whoisServer=item['Registrar_WHOIS_Server'])
	else:
	    url_search = "http://whois.chinaz.com/?Domain={domain}&isforceupdate=1".format(domain=item['DOMAIN'])
        domain_list = selector.xpath('//a[@class="col-gray03 fz18 pr5"]/text()').extract()
        if domain_list == []:
            return scrapy.Request(url_search,meta={"item":item,"flag":flag+1},callback=self.parse_whoischinaz,dont_filter=True)
        if flag == 0:
	    Detail_Dict = selector.xpath('//script[@type="text/javascript"]/text()').re(r"data: { domain:(.*),whoisServer:(.*),deskey:(.*),isupdate:(.*)}")
	    formdata_list = [i.replace(" ","").replace("'","") for i in Detail_Dict]
	    formdata = dict(domain=formdata_list[0],whoisServer=formdata_list[1],deskey=formdata_list[2],isupdate="")
	    return scrapy.http.FormRequest("http://whois.chinaz.com/getDetailInfo.ashx",formdata=formdata,meta={"item":item},callback=self.parse_detail)

        ro_list = selector.xpath('//div[@class="block ball"]/span/text()').extract()
        rw_list = selector.xpath('//div[@class="fr WhLeList-right"]/span/text()').extract()
        try:
            item['Registrar'] = ro_list[0].encode("utf8")
            item['Registrant_Organization'] = ro_list[1].encode("utf8")
            item['Updated_Date'] = rw_list[0].encode("utf8")
            item['Registrar_WHOIS_Server'] = rw_list[-1].encode("utf8")
        except Exception,e:
            self.logger.warning(e)
	    traceback.print_exc()
        
        detail_selector = selector.xpath('//p[@id="detail_info"]/text()')    
        try:
	    item["Registrant_City"] = detail_selector.re('Registrant City: \w+')[0].split(":")[1].replace(' ','').encode("utf8")
            item["Registrant_State"] = detail_selector.re('Registrant State/Province: \w+')[0].split(":")[1].replace(' ','').encode("utf8")
            item["Registrant_Postal_Code"] = detail_selector.re('Registrant Postal Code: \w+')[0].split(":")[1].replace(' ','').encode("utf8")
            item["Registrant_Country"] = detail_selector.re('Registrant Country: \w+')[0].split(":")[1].replace(' ','').encode("utf8")

	    self.logger.info('Parse_WHOIS function called on {domain} of {num}'.format(domain=item['DOMAIN'],num=item["NUM"]))
            return scrapy.http.FormRequest("http://whois.chinaz.com/getTitleInfo.ashx",formdata={"host":item["DOMAIN"],"isupdate":"1"},meta={"item":item},callback=self.parse_key)
        except Exception,e:
            self.logger.warning(e)
	    traceback.print_exc()
	    self.logger.info('Parse_WHOIS function called on {domain} of {num}'.format(domain=item['DOMAIN'],num=item["NUM"]))
            return scrapy.Request(url_search, meta={"item":item,"flag":flag+1}, callback=self.parse_whoischinaz,dont_filter=True)

    def parse_key(self,response):
	selector = scrapy.Selector(response=response)
	item = response.meta["item"]
	td_list = selector.xpath('//p/text()').extract()
        kk_list = selector.xpath('//p[@class="keyci"]/a/text()').extract()
        try:
            item['KEY_Title'] = td_list[0].encode("utf8")
            item['KEY_Description'] = td_list[1].encode("utf8")
            item['KEY_KeyWords'] = ",".join(kk_list).encode("utf8")
        except Exception,e:
            self.logger.warning(e)
            traceback.print_exc()
	finally:
	    self.logger.info('Parse_KEY function called on {domain} of {num}'.format(domain=item['DOMAIN'],num=item["NUM"]))
	    return item

    def parse_detail(self,response):
	selector = scrapy.Selector(response=response)
        item = response.meta["item"]

	try:
	    item["Registrant_City"] = selector.xpath('//p/text()').re('Registrant City: \w+')[0].split(":")[1].replace(' ','').encode("utf8")
	    item["Registrant_State"] = selector.xpath('//p/text()').re('Registrant State/Province: \w+')[0].split(":")[1].replace(' ','').encode("utf8")
	    item["Registrant_Postal_Code"] = selector.xpath('//p/text()').re('Registrant Postal Code: \w+')[0].split(":")[1].replace(' ','').encode("utf8")
	    item["Registrant_Country"] = selector.xpath('//p/text()').re('Registrant Country: \w+')[0].split(":")[1].replace(' ','').encode("utf8")
	except Exception,e:
	    self.logger.warning(e)
	    traceback.print_exc()
	finally:
	    url_search = "http://whois.chinaz.com/{domain}".format(domain=item['DOMAIN'])
	    return scrapy.Request(url_search, meta={"item":item,"flag":1}, callback=self.parse_whoischinaz,dont_filter=True) 
