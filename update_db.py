# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:13:20 2020

@author: sqr_p
"""

import pymongo
from main import mp
import json
from bson.decimal128 import Decimal128

print('正在更新数据库...')
dbclient = pymongo.MongoClient('SERVER')
db = dbclient['Arknights_OneGraph']

db_Material, db_Stage = db['Material'], db['Stage']
[mp.output_best_stage(x) for x in '123']
for item in db_Material.find():
    if 'credit_store_value' in item:
        if item['name'] in mp.best_stage:
            db_Material.update_one({'_id': item['_id']},
                {'$set': {'credit_store_value': Decimal128('%.3f'%(100*mp.creditEffect[item['name']])),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': mp.best_stage[item['name']]['lowest_ap_stages'],
                          'balanced_stages': mp.best_stage[item['name']]['balanced_stages'],
                          'drop_rate_first_stages': mp.best_stage[item['name']]['drop_rate_first_stages']}
                })
        else:
            db_Material.update_one({'_id': item['_id']},
                {'$set': {'credit_store_value': Decimal128('%.3f'%(100*mp.creditEffect[item['name']])),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': [{}],
                          'balanced_stages': [{}],
                          'drop_rate_first_stages': [{}]}
                })
    if 'green_ticket_value' in item:
        if item['name'] in mp.best_stage:
            db_Material.update_one({'_id': item['_id']},
                {'$set': {'green_ticket_value': Decimal128('%.3f'%(mp.greenTickets[item['name']])),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': mp.best_stage[item['name']]['lowest_ap_stages'],
                          'balanced_stages': mp.best_stage[item['name']]['balanced_stages'],
                          'drop_rate_first_stages': mp.best_stage[item['name']]['drop_rate_first_stages']}})
        else:
            db_Material.update_one({'_id': item['_id']},
                {'$set': {'green_ticket_value': Decimal128('%.3f'%(mp.greenTickets[item['name']])),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': [{}],
                          'balanced_stages': [{}],
                          'drop_rate_first_stages': [{}]}})
    if 'golden_ticket_value' in item:
        db_Material.update_one({'_id': item['_id']},
                {'$set': {'golden_ticket_value': Decimal128('%.3f'%(mp.yellowTickets[item['name']])),
                          'Notes': mp.Notes[item['name']]}})

print('更新完成.')