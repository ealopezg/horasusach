# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from rusach.items import SchoolItem,ProgramItem

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



class RusachPipeline:
    def process_item(self, item, spider):
        if isinstance(item, SchoolItem):
            return self.handle_school(item,spider)
        if isinstance(item,ProgramItem):
            return self.handle_program(item,spider)

    def handle_school(self,item,spider):
        self.db.collection('schools').document(item['id']).set({'name': item['name']})
        
        for program in item['programs']:
            self.db.collection('schools',item['id'],'programs').document(program['id_program']).set({'name':program['name'],'hidden': False})
        return item

    def handle_program(self,item,spider):
        self.db.collection(u'schedules').document(item['id_school']+'_'+item['id_program']+'_'+item['period']).set(ItemAdapter(item).asdict())
        return item
    
    def open_spider(self, spider):
        cred = credentials.Certificate("/Users/ealopezg/horario-usach-af4f2-firebase-adminsdk-f6z49-f73e7e9ffa.json")
        firebase_admin.initialize_app(cred, {
            'projectId': 'horario-usach-af4f2'
        })
        self.db = firestore.client()
