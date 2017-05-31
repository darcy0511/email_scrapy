# -*- coding: utf-8 -*-
import scrapy
import subprocess
from email_db.items import ChinazWhoisDbItem
import re


domain_name_re = re.compile(r'Domain Name:\s?(.+)',re.IGNORECASE)
registrant_name_re = re.compile(r'Registrant Name:\s?(.+)',re.IGNORECASE)
registrant_organization_re = re.compile(r'Registrant Organization:\s?(.+)',re.IGNORECASE)
registrant_street_re = re.compile(r'Registrant Street:\s?(.+)',re.IGNORECASE)
registrant_city_re = re.compile(r'Registrant City:\s?(.+)',re.IGNORECASE)
registrant_state_re = re.compile(r'Registrant State/Province:\s?(.+)',re.IGNORECASE)
registrant_postal_re = re.compile(r'Registrant Postal Code:\s?(.+)',re.IGNORECASE)
registrant_country_re = re.compile(r'Registrant Country:\s?(.+)',re.IGNORECASE)

class ChinazWhoisSpider(scrapy.Spider):
    name = "chinaz_whois"
    allowed_domains = ["baidu.com"]
    start_urls = ['http://www.qq.com/']


    def __init__(self, filepath='/home/yyb/py_env/scrapy_email_code/email_db/email_data/reg_lower.csv', minloc='0', maxloc='0', *args, **kwargs):
        super(ChinazWhoisSpider, self).__init__(*args, **kwargs)
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

                    p = subprocess.Popen(['whois', line], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    yield scrapy.Request("http://www.qq.com/", meta={"num":num,'domain':line,'domain_data':p},dont_filter=True ,callback=self.parse_whoischinaz)

    def parse_whoischinaz(self, response):
        p = response.meta['domain_data']
        r = p.communicate()[0]
	
        if domain_name_re.findall(r)==[] or domain_name_re.findall(r)==None:
            return

        item = ChinazWhoisDbItem()
        item["NUM"] = response.meta['num']
        item["DOMAIN"] = response.meta['domain']
        item['Registrant_Name'] = registrant_name_re.findall(r)[0] if registrant_name_re.findall(r)!=[] else ''
        item['Registrant_Organization'] = registrant_organization_re.findall(r)[0] if registrant_organization_re.findall(r)!=[] else ''
        item['Registrant_City'] = registrant_city_re.findall(r)[0] if registrant_city_re.findall(r)!=[] else ''
        item['Registrant_State'] = registrant_state_re.findall(r)[0] if registrant_state_re.findall(r)!=[] else ''
        item['Registrant_Country'] = registrant_country_re.findall(r)[0] if registrant_country_re.findall(r)!=[] else ''
        item['Registrant_Postal_Code'] = registrant_postal_re.findall(r)[0] if registrant_postal_re.findall(r)!=[] else ''
        item['Registrant_Street'] = registrant_street_re.findall(r)[0] if registrant_street_re.findall(r)!=[] else ''

        return item          
