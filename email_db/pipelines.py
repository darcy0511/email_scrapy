# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import os
from email_db.items import EmailDbItem

class EmailDbPipeline(object):
    filepath = os.path.join(os.getcwd(),'email_data')

    def open_spider(self, spider):
	if not os.path.exists(self.filepath):
            os.mkdir(self.filepath) 
        filename = os.path.join(self.filepath,'EmailDb_results.csv')
        self.file = open(filename,'wb')
        fieldnames = list(EmailDbItem.fields.keys())
        self.writer = csv.DictWriter(self.file,fieldnames=fieldnames,delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        self.writer.writeheader()
	#self.file = open(filename, 'wb')

    def close_spider(self, spider):
        self.file.close()
	
    def process_item(self, item, spider):
	self.writer.writerow(dict(item))
	#print dict(item)
        #line = json.dumps(dict(item)) + "\n"
        #self.file.write(line)
	#print('Pipeline function called on %s',line) 
	return item
