# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:13:20 2020

@author: sqr_p
"""

import pymongo
from main import mp
from bson.decimal128 import Decimal128
import time
import pytz
from dateutil import parser


print('正在更新数据库...')
dbclient = pymongo.MongoClient('SERVER')
db = dbclient['Arknights_OneGraph']

db_Material, db_Stage = db['Material'], db['Stage']
[mp.output_best_stage(x) for x in '123']
update_time = parser.parse(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))
for item in db_Material.find():
    if 'credit_store_value' in item:
        if item['name'] in mp.best_stage:
            db_Material.update_one({'_id': item['_id']},
                {'$set': {'credit_store_value': Decimal128('%.3f'%(100*mp.creditEffect[item['name']])),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': mp.best_stage[item['name']]['lowest_ap_stages'],
                          'balanced_stages': mp.best_stage[item['name']]['balanced_stages'],
                          'drop_rate_first_stages': mp.best_stage[item['name']]['drop_rate_first_stages'],
                          'last_updated': update_time}
                })
        else:
            db_Material.update_one({'_id': item['_id']},
                {'$set': {'credit_store_value': Decimal128('%.3f'%(100*mp.creditEffect[item['name']])),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': [{}],
                          'balanced_stages': [{}],
                          'drop_rate_first_stages': [{}],
                          'last_updated': update_time}
                })
    if 'green_ticket_value' in item:
        if item['name'] in mp.best_stage:
            db_Material.update_one({'_id': item['_id']},
                {'$set': {'green_ticket_value': Decimal128('%.3f'%(mp.greenTickets[item['name']])),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': mp.best_stage[item['name']]['lowest_ap_stages'],
                          'balanced_stages': mp.best_stage[item['name']]['balanced_stages'],
                          'drop_rate_first_stages': mp.best_stage[item['name']]['drop_rate_first_stages'],
                          'last_updated': update_time}})
        else:
            db_Material.update_one({'_id': item['_id']},
                {'$set': {'green_ticket_value': Decimal128('%.3f'%(mp.greenTickets[item['name']])),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': [{}],
                          'balanced_stages': [{}],
                          'drop_rate_first_stages': [{}],
                          'last_updated': update_time}})
    if 'golden_ticket_value' in item:
        db_Material.update_one({'_id': item['_id']},
                {'$set': {'golden_ticket_value': Decimal128('%.3f'%(mp.yellowTickets[item['name']])),
                          'Notes': mp.Notes[item['name']],
                          'last_updated': update_time}})

print('更新完成.')