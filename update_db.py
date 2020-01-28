# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:13:20 2020

@author: sqr_p
"""

import pymongo
from main import mp
from bson.decimal128 import Decimal128

print('正在更新数据库...')
dbclient = pymongo.MongoClient('Server')
db = dbclient['Arknights_OneGraph']

db_Material, db_Stage = db['Material'], db['Stage']

for item in db_Material.find():
    if 'credit_store_value' in item:
        db_Material.update_one({'_id': item['_id']},
                {'$set': {'credit_store_value': Decimal128('%.3f'%(100*mp.creditEffect[item['name']])),
                          'Notes': mp.Notes[item['name']]}})
    if 'green_ticket_value' in item:
        db_Material.update_one({'_id': item['_id']},
                {'$set': {'green_ticket_value': Decimal128('%.3f'%(mp.greenTickets[item['name']])),
                          'Notes': mp.Notes[item['name']]}})
    if 'golden_ticket_value' in item:
        db_Material.update_one({'_id': item['_id']},
                {'$set': {'golden_ticket_value': Decimal128('%.3f'%(mp.yellowTickets[item['name']])),
                          'Notes': mp.Notes[item['name']]}})

print('更新完成.')