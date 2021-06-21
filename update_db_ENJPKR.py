# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:13:20 2020

@author: sqr_p
"""

import pymongo
from MaterialPlanning import MaterialPlanning
import time
from dateutil import parser
from utils import required_dctENJPKR, owned_dct, aggregation, collectionENJPKR

aggregation(collectionENJPKR,required_dctENJPKR,"Amiya")

update_time = parser.parse(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))
print(update_time)
print('正在从企鹅物流获取数据...')
server = open('data/server.txt', 'r').readline().strip()
dbclient = pymongo.MongoClient(server)
db = dbclient['Arknights_OneGraph']

Filter_special_items = ['荒芜行动物资补给', '罗德岛物资补给', '岁过华灯', '32h战略配给', '感谢庆典物资补给']
Filter_special_stages = ['S4-4', 'S6-4','S4-9']+ ['SK-%d'%x for x in range(1, 6)]

# Calculation for EN, JP and KR server
collection = db['Material_ENJPKR']
StagesNotAval = ['7-%d'%x for x in range(1, 19)]+['S7-1', 'S7-2']+['RI-%d'%x for x in range(1, 9)] #chapter 7
StagesNotAval.extend(['R8-%d'%x for x in range(1, 12)] + ['M8-6', 'M8-7', 'M8-8'] + ['JT8-%d'%x for x in range(1, 4)])
print(StagesNotAval)
Event_Stages = ['FA-%d'%x for x in range(1, 9)]
mp_event = MaterialPlanning(filter_stages=Filter_special_stages + Filter_special_items+StagesNotAval,
                      filter_freq=100,
                      update=True,
                      printSetting='000011101100'
                      )
mp_event.get_plan(required_dctENJPKR, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)
mp = MaterialPlanning(filter_stages=Filter_special_stages + Filter_special_items + Event_Stages+StagesNotAval,
                      filter_freq=100,
                      update=True,
                      printSetting='000011101100'
                      )
mp.get_plan(required_dctENJPKR, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)
[mp_event.output_best_stage(x) for x in '123']
[mp.output_best_stage(x) for x in '123']
print('正在更新EN, JP和KR服数据库')
for k, v in sorted(mp.effect.items(), key=lambda x: x[1], reverse=True):
    print(f'已更新关卡{k}, 效率{100*v:.2f}', end=' ')
    db['StagesENJPKR'].update_one({'code': k}, {'$set': {'efficiency': v , 'sampleSize': mp.stage_times[k]}},upsert=True)

for item in collection.find():
    x = item['name']
    print('已更新%s\t' % x, end='\t')
    collection.update_one({'_id': item['_id']},
                          {'$set': {'contingency_store_value': {'infinite': '%.3f'%mp.HeYueDict[x] if x in mp.HeYueDict else '0.0',
                                                                'finite': '%.3f'%mp.HYODict[x] if x in mp.HYODict else '0.0'}}
            },upsert=True)

    if 'credit_store_value' in item:
        if item['name'] in mp.best_stage:
            collection.update_one({'_id': item['_id']},
                {'$set': {'credit_store_value': {'event': '%.3f'%(100*mp_event.creditEffect[item['name']]),
                                                 'normal': '%.3f'%(100*mp.creditEffect[item['name']])},
                          'Notes': {'event': mp_event.Notes[item['name']],
                                    'normal': mp.Notes[item['name']]},
                          'lowest_ap_stages': {'event': mp_event.best_stage[item['name']]['lowest_ap_stages'],
                                               'normal': mp.best_stage[item['name']]['lowest_ap_stages']},
                          'balanced_stages': {'event': mp_event.best_stage[item['name']]['balanced_stages'],
                                              'normal': mp.best_stage[item['name']]['balanced_stages']},
                          'drop_rate_first_stages': {'event': mp_event.best_stage[item['name']]['drop_rate_first_stages'],
                                                     'normal': mp.best_stage[item['name']]['drop_rate_first_stages']},
                          'last_updated': update_time
                         }
                },upsert=True)
        else:
            collection.update_one({'_id': item['_id']},
                {'$set': {'credit_store_value': {'event': '%.3f'%(100*mp_event.creditEffect[item['name']]),
                                                 'normal': '%.3f'%(100*mp.creditEffect[item['name']])},
                          'Notes': {'event': mp_event.Notes[item['name']],
                                    'normal': mp.Notes[item['name']]},
                          'lowest_ap_stages': {'event': [],
                                               'normal': []},
                          'balanced_stages': {'event': [],
                                               'normal': []},
                          'drop_rate_first_stages': {'event': [],
                                               'normal': []},
                          'last_updated': update_time}
                },upsert=True)
    if 'green_ticket_value' in item:
        if item['name'] in mp.best_stage:
            collection.update_one({'_id': item['_id']},
                {'$set': {'green_ticket_value': {'event': '%.3f'%(mp_event.greenTickets[item['name']]),
                                                 'normal': '%.3f'%(mp.greenTickets[item['name']])},
                          'Notes': {'event': mp_event.Notes[item['name']],
                                    'normal': mp.Notes[item['name']]},
                          'lowest_ap_stages': {'event': mp_event.best_stage[item['name']]['lowest_ap_stages'],
                                               'normal': mp.best_stage[item['name']]['lowest_ap_stages']},
                          'balanced_stages': {'event': mp_event.best_stage[item['name']]['balanced_stages'],
                                              'normal': mp.best_stage[item['name']]['balanced_stages']},
                          'drop_rate_first_stages': {'event': mp_event.best_stage[item['name']]['drop_rate_first_stages'],
                                                     'normal': mp.best_stage[item['name']]['drop_rate_first_stages']},
                          'last_updated': update_time}},upsert=True)
        else:
            collection.update_one({'_id': item['_id']},
                {'$set': {'green_ticket_value': {'event': '%.3f'%(mp_event.greenTickets[item['name']]),
                                                 'normal': '%.3f'%(mp.greenTickets[item['name']])},
                          'Notes': {'event': mp_event.Notes[item['name']],
                                    'normal': mp.Notes[item['name']]},
                          'lowest_ap_stages': {'event': [],
                                               'normal': []},
                          'balanced_stages': {'event': [],
                                               'normal': []},
                          'drop_rate_first_stages': {'event': [],
                                               'normal': []},
                          'last_updated': update_time}},upsert=True)
    if 'golden_ticket_value' in item:
        collection.update_one({'_id': item['_id']},
                {'$set': {'golden_ticket_value': {'event': '%.3f'%(mp_event.yellowTickets[item['name']]),
                                                 'normal': '%.3f'%(mp.yellowTickets[item['name']])},
                          'Notes': {'event': mp_event.Notes[item['name']],
                                    'normal': mp.Notes[item['name']]},
                          'last_updated': update_time}},upsert=True)

print('\nEn,JP,KR服更新完成.')
