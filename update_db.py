# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:13:20 2020

@author: sqr_p
"""

import pymongo
from MaterialPlanning import MaterialPlanning
import time
from dateutil import parser
from utils import required_dct, owned_dct

print('正在从企鹅物流获取数据...')
server = open('data/server.txt', 'r').readline().strip()
dbclient = pymongo.MongoClient(server)
db = dbclient['Arknights_OneGraph']
collection = db['Material']

Event_Stages = ['SA-%d'%x for x in range(1,7)]
update_time = parser.parse(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))
mp_event = MaterialPlanning(filter_stages=['S4-4', 'S6-4'],
                      filter_freq=100,
                      update=True,
                      printSetting='0000110011'
                      )
mp_event.get_plan(required_dct, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)
mp = MaterialPlanning(filter_stages=['S4-4', 'S6-4'] + Event_Stages,
                      filter_freq=100,
                      update=False,
                      printSetting='0000110011'
                      )
mp.get_plan(required_dct, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)

[mp_event.output_best_stage(x) for x in '123']
[mp.output_best_stage(x) for x in '123']

print('正在更新数据库...')
for item in collection.find():
    x = item['name']
    print('\r已更新%s\t' % x, end='\t')
    if item['name'] in mp.HeYueDict or item['name'] in mp.HYODict:
        collection.update_one({'_id': item['_id']},
                              {'$set': {'contingency_store_value': {'infinite': '%.3f'%mp.HeYueDict[x] if x in mp.HeYueDict else '0.0',
                                                                    'finite': '%.3f'%mp.HYODict[x] if x in mp.HYODict else '0.0'}}
                })
    if 'credit_store_value' in item:
        if item['name'] in mp.best_stage:
            collection.update_one({'_id': item['_id']},
                {'$set': {'credit_store_value' : '%.3f'%(100*mp.creditEffect[item['name']]),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': mp.best_stage[item['name']]['lowest_ap_stages'],
                          'balanced_stages': mp.best_stage[item['name']]['balanced_stages'],
                          'drop_rate_first_stages': mp.best_stage[item['name']]['drop_rate_first_stages'],
                          'last_updated': update_time}
                })
        else:
            collection.update_one({'_id': item['_id']},
                {'$set': {'credit_store_value': '%.3f'%(100*mp.creditEffect[item['name']]),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': [{}],
                          'balanced_stages': [{}],
                          'drop_rate_first_stages': [{}],
                          'last_updated': update_time}
                })
    if 'green_ticket_value' in item:
        if item['name'] in mp.best_stage:
            collection.update_one({'_id': item['_id']},
                {'$set': {'green_ticket_value': '%.3f'%(mp.greenTickets[item['name']]),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': mp.best_stage[item['name']]['lowest_ap_stages'],
                          'balanced_stages': mp.best_stage[item['name']]['balanced_stages'],
                          'drop_rate_first_stages': mp.best_stage[item['name']]['drop_rate_first_stages'],
                          'last_updated': update_time}})
        else:
            collection.update_one({'_id': item['_id']},
                {'$set': {'green_ticket_value': '%.3f'%(mp.greenTickets[item['name']]),
                          'Notes': mp.Notes[item['name']],
                          'lowest_ap_stages': [{}],
                          'balanced_stages': [{}],
                          'drop_rate_first_stages': [{}],
                          'last_updated': update_time}})
    if 'golden_ticket_value' in item:
        collection.update_one({'_id': item['_id']},
                {'$set': {'golden_ticket_value': '%.3f'%(mp.yellowTickets[item['name']]),
                          'Notes': mp.Notes[item['name']],
                          'last_updated': update_time}})

print('\n更新完成.')
