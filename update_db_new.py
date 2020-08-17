# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:13:20 2020

@author: sqr_p
"""

import pymongo
from MaterialPlanning import MaterialPlanning
import time
from dateutil import parser
from utils import required_dctCN, owned_dct

update_time = parser.parse(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))
print(update_time)
print('正在从企鹅物流获取数据...')
server = open('data/server.txt', 'r').readline().strip()
dbclient = pymongo.MongoClient(server)
db = dbclient['Arknights_OneGraph']

Filter_special_items = ['荒芜行动物资补给', '罗德岛物资补给', '岁过华灯', '32h战略配给']
Filter_special_stages = ['S4-4', 'S6-4','S4-9']

# Calculation for CN server
collection = db['Material_Event']
Event_Stages = ['TW-%d'%x for x in range(1,9)]
mp_event = MaterialPlanning(filter_stages=Filter_special_stages + Filter_special_items,
                      filter_freq=100,
                      update=True,
                      printSetting='000011101111',CCSeason=2
                      )
mp_event.get_plan(required_dctCN, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)

mp = MaterialPlanning(filter_stages=Filter_special_stages + Filter_special_items + Event_Stages,
                      filter_freq=100,
                      update=True,
                      printSetting='000011101111',CCSeason=2
                      )
mp.get_plan(required_dctCN, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)
[mp_event.output_best_stage(x) for x in '123']
[mp.output_best_stage(x) for x in '123']
print('正在更新CN服数据库')
for k, v in sorted(mp.effect.items(), key=lambda x: x[1], reverse=True):
    print(f'已更新关卡{k}, 效率{100*v:.2f}', end=' ')
    db['Stages'].update_one({'code': k}, {'$set': {'efficiency': v , 'sampleSize': mp.stage_times[k]}},upsert=True)


for item in collection.find():
    x = item['name']
    print('已更新%s\t' % x, end='\t')

    collection.update_one({'_id': item['_id']},
                          {'$set': {'contingency_store_value': {'infinite': '%.3f'%mp.HeYueDict[x] if x in mp.HeYueDict else '0.0',
                                                                'finite': '%.3f'%mp.HYODict[x] if x in mp.HYODict else '0.0'}}
            })
    if item['name'] in mp.orangeTickets:
        collection.update_one({'_id': item['_id']},
                  {'$set': {'orange_store_value': {'event': '%.3f'%mp_event.orangeTickets[item['name']],
                                                   'normal': '%.3f'%mp.orangeTickets[item['name']]},
                            'orange_note': {'event': mp_event.orangeNotes[item['name']],
                                            'normal': mp.orangeNotes[item['name']]}
                           }
                  })
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
                })
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
                })
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
                          'last_updated': update_time}})
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
                          'last_updated': update_time}})
    if 'golden_ticket_value' in item:
        collection.update_one({'_id': item['_id']},
                {'$set': {'golden_ticket_value': {'event': '%.3f'%(mp_event.yellowTickets[item['name']]),
                                                 'normal': '%.3f'%(mp.yellowTickets[item['name']])},
                          'Notes': {'event': mp_event.Notes[item['name']],
                                    'normal': mp.Notes[item['name']]},
                          'last_updated': update_time}})

print('\nCN服更新完成.')
