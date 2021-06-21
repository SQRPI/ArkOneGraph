# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:13:20 2020

@author: sqr_p
"""
import io
import sys

from discord_webhook import DiscordWebhook, DiscordEmbed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码
import pymongo
from MaterialPlanning import MaterialPlanning
import time
from dateutil import parser
from utils import required_dctCN, owned_dct, aggregation, collectionCN

CCSeason = 5

aggregation(collectionCN, required_dctCN, "阿米娅")
update_time = parser.parse(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))
print(update_time)
print('正在从企鹅物流获取数据...')
server = open('data/server.txt', 'r').readline().strip()
dbclient = pymongo.MongoClient(server)
db = dbclient['Arknights_OneGraph']
message = """Error when updating arkonegraph"""
webhookURL = open('data/webhook.txt', 'r').readline().strip()
webhook = DiscordWebhook(url=webhookURL)
InjectNew = True

Filter_special_items = ['荒芜行动物资补给', '罗德岛物资补给', '岁过华灯', '32h战略配给', '感谢庆典物资补给',
                        '应急理智小样', '黄铁行动物资补给', '利刃行动物资补给', '燃灰行动物资补给']
Filter_special_stages = ['S4-4', 'S6-4', 'S4-9']+['DM-%d'%x for x in range(1, 11)]+['GT-%d'%x for x in range(1, 11)]+\
                        ['OF-F%d'%x for x in range(1, 11)]+['SV-%d'%x for x in range(1, 11)]+['WD-%d'%x for x in range(1, 11)]

# Calculation for CN server
collection = db['Material_Event']
collection_exp = db['Material_Event_exp']


# Get current event initials
# OF is officially 0 value stages.
currrent_event_raw = db['Activities'].find_one({'live': True})
if not currrent_event_raw:
    currrent_event = "OF"
else:
    currrent_event = currrent_event_raw['initials']

Event_Stages = [(currrent_event+'-%d')%x for x in range(1, 9)]

# Event planning w/out base
mp_event = MaterialPlanning(filter_stages=Filter_special_stages + Filter_special_items,
                      filter_freq=100,
                      update=True,
                      printSetting='111111111111',CCSeason=CCSeason
                      )
mp_event.get_plan(required_dctCN, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)

# Event planning w/ base
mp_event_base = MaterialPlanning(filter_stages=Filter_special_stages + Filter_special_items,
                      filter_freq=100,
                      update=True,
                      printSetting='111111111111',CCSeason=CCSeason,
                      ExpFromBase=True
                      )
mp_event_base.get_plan(required_dctCN, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)


# Regular planning w/ base
mp_expFromBase = MaterialPlanning(filter_stages=Filter_special_stages + Filter_special_items + Event_Stages,
                      filter_freq=100,
                      update=False,
                      printSetting='111111111111',CCSeason=CCSeason,
                      ExpFromBase=True
                      )
mp_expFromBase.get_plan(required_dctCN, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)

# Regular planning w/out base
mp = MaterialPlanning(filter_stages=Filter_special_stages + Filter_special_items + Event_Stages,
                      filter_freq=100,
                      update=False,
                      printSetting='111111111111',CCSeason=CCSeason
                      )
mp.get_plan(required_dctCN, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)

# mp = mp_expFromBase

[mp_event.output_best_stage(x) for x in '123']
[mp.output_best_stage(x) for x in '123']
[mp_event_base.output_best_stage(x) for x in '123']
[mp_expFromBase.output_best_stage(x) for x in '123']

def find_correct_stage_ID(code):
    for item in list(mp.stage_list.keys()):
        if mp.stage_list[item]['code'] == code:
            return item


# Write in the db for Stages
print(mp.stage_list)
print(mp.stage_dct_rv)
print('正在更新CN服数据库')


for k, v in sorted(mp.effect.items(), key=lambda x: x[1], reverse=True):
    print(f'已更新关卡{k}, 效率{100*v:.2f}', end=' ')
    # db['Stages'].update_one({'stage_id':list(mp.stage_list.keys())[k]}, {'$set': {'code': mp.stage_array[k],'efficiency': v , 'sampleSize': mp.stage_times[k]}},upsert=True)
    db['Stages'].update_one({'code': k}, {'$set': {'efficiency': v , 'sampleSize': mp.stage_times[k]}},upsert=True)

for k, v in sorted(mp_event.effect.items(), key=lambda x: x[1], reverse=True):
    print(f'已更新关卡{k}, 效率{100*v:.2f}', end=' ')
    # db['Stages'].update_one({'stage_id':list()[k]}, {'$set': {'code': mp.stage_array[k],'efficiency_event': v , 'sampleSize': mp.stage_times[k]}},upsert=True)
    db['Stages'].update_one({'code': k}, {'$set': {'efficiency_event': v, 'sampleSize': mp.stage_times[k]}}, upsert=True)

for k, v in sorted(mp_expFromBase.effect.items(), key=lambda x: x[1], reverse=True):
    print(f'已更新关卡{k}, 效率{100*v:.2f}', end=' ')
    # db['Stages'].update_one({'stage_id':list(mp.stage_list.keys())[k]}, {'$set': {'code': mp.stage_array [k],'efficiency_base': v , 'sampleSize': mp.stage_times[k]}},upsert=True)
    db['Stages'].update_one({'code': k}, {
        '$set': {'efficiency_base': v, 'sampleSize': mp.stage_times[k]}}, upsert=True)

for k, v in sorted(mp_event_base.effect.items(), key=lambda x: x[1], reverse=True):
    print(f'已更新关卡{k}, 效率{100*v:.2f}', end=' ')
    # db['Stages'].update_one({'stage_id':list(mp.stage_list.keys())[k]}, {'$set': {'code': mp.stage_array[k],'efficiency_event_base': v , 'sampleSize': mp.stage_times[k]}},upsert=True)
    db['Stages'].update_one({'code': k}, {'$set': {'efficiency_event_base': v , 'sampleSize': mp.stage_times[k]}},upsert=True)

# Write in the db, without considering income from base
# Old version -> separate dbs
for item in collection.find():
    x = item['name']
    print(x in mp.HeYueDict)
    print('已更新%s\t' % x, end='\t')
    if x == "术师，特种，医疗或先锋芯片":
        collection.update_one({'_id': item['_id']},
                              {'$set': {'contingency_store_value': {
                                  'infinite': '%.3f' % mp.HeYueDict[x],
                                  'finite': '0.0'}}}, upsert=InjectNew)
    elif item == "近卫，狙击，辅助或重装芯片":
        collection.update_one({'_id': item['_id']},
                              {'$set': {'contingency_store_value': {
                                  'infinite': '%.3f' % mp.HeYueDict[x],
                                  'finite': '0.0'}}}, upsert=InjectNew)
    else:
        collection.update_one({'_id': item['_id']},
                              {'$set': {'contingency_store_value': {'infinite': '%.3f'%mp.HeYueDict[x] if x in mp.HeYueDict else '0.0',
                                                                    'finite': '%.3f'%mp.HYODict[x] if x in mp.HYODict else '0.0',
                                                                   }}},
                          upsert=InjectNew)
    #     Update golden cert store
    if item['name'] in mp.orangeTickets:
        collection.update_one({'_id': item['_id']},
                  {'$set': {'orange_store_value': {'event': '%.3f'%mp_event.orangeTickets[item['name']],
                                                   'normal': '%.3f'%mp.orangeTickets[item['name']]},
                            'orange_note': {'event':  mp_event.orangeNotes[item['name']],
                                            'normal': mp.orangeNotes[item['name']]}
                           }
                  },upsert=InjectNew)
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
                },upsert=InjectNew)
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
                },upsert=InjectNew)
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
                          'last_updated': update_time}},upsert=InjectNew)
    if 'golden_ticket_value' in item:
        collection.update_one({'_id': item['_id']},
                {'$set': {'golden_ticket_value': {'event': '%.3f'%(mp_event.yellowTickets[item['name']]),
                                                 'normal': '%.3f'%(mp.yellowTickets[item['name']])},
                          'Notes': {'event': mp_event.Notes[item['name']],
                                    'normal': mp.Notes[item['name']]},
                          'last_updated': update_time}},upsert=InjectNew)
    if item['name'] in mp.purpleTickets:
        collection.update_one({'_id': item['_id']},
                              {'$set': {'purple_ticket_value': {'event': '%.3f' % mp_event.purpleTickets[item['name']],
                                                               'normal': '%.3f' % mp.purpleTickets[item['name']]},
                                        'purple_note': {'event': mp_event.purpleNotes[item['name']],
                                                        'normal': mp.purpleNotes[item['name']]}
                                        }
                               }, upsert=InjectNew)





# Write in the db, without considering income from base
# New version -> same db with more jsons
# for item in collection.find():
#     x = item['name']
#     print(x in mp.HeYueDict)
#     print('已更新%s\t' % x, end='\t')
#     if x == "术师，特种，医疗或先锋芯片":
#         collection.update_one({'_id': item['_id']},
#                               {'$set': {'contingency_store_value': {
#                                   'infinite': '%.3f' % mp.HeYueDict[x],
#                                   'infinite_base': '%.3f' % mp_expFromBase.HeYueDict[x],
#                                   'finite': '0.0'}}}, upsert=InjectNew)
#     elif item == "近卫，狙击，辅助或重装芯片":
#         collection.update_one({'_id': item['_id']},
#                               {'$set': {'contingency_store_value': {
#                                   'infinite': '%.3f' % mp.HeYueDict[x],
#                                   'infinite_base' : '%.3f' % mp_expFromBase.HeYueDict[x],
#                                   'finite': '0.0'}}}, upsert=InjectNew)
#     else:
#         collection.update_one({'_id': item['_id']},
#                               {'$set': {'contingency_store_value': {'infinite': '%.3f'%mp.HeYueDict[x] if x in mp.HeYueDict else '0.0',
#                                                                     'finite': '%.3f'%mp.HYODict[x] if x in mp.HYODict else '0.0',
#                                                                     'infinite_base': '%.3f'%mp_expFromBase.HeYueDict[x] if x in mp.HeYueDict else '0.0',
#                                                                     'finite_base': '%.3f'%mp_expFromBase.HYODict[x] if x in mp.HYODict else '0.0'}}},
#                           upsert=InjectNew)
#     #     Update golden cert store
#     if item['name'] in mp.orangeTickets:
#         collection.update_one({'_id': item['_id']},
#                   {'$set': {'orange_store_value': {'event': {'nobase':'%.3f'%mp_event.orangeTickets[item['name']],'base':'%.3f'%mp_event_base.orangeTickets[item['name']]},
#                                                    'normal': {'nobase':'%.3f'%mp.orangeTickets[item['name']],'base':'%.3f'%mp_expFromBase.orangeTickets[item['name']]}},
#                             'orange_note': {'event': {'nobase': mp_event.orangeNotes[item['name']], 'base': mp_event_base.orangeNotes[item['name']]},
#                                             'normal': {'nobase':mp.orangeNotes[item['name']], 'base': mp_expFromBase.orangeNotes[item['name']]}}
#                            }
#                   },upsert=InjectNew)
#     if 'credit_store_value' in item:
#         if item['name'] in mp.best_stage:
#             collection.update_one({'_id': item['_id']},
#                 {'$set': {'credit_store_value': {'event': '%.3f'%(100*mp_event.creditEffect[item['name']]),
#                                                  'normal': '%.3f'%(100*mp.creditEffect[item['name']])},
#                           'Notes': {'event': mp_event.Notes[item['name']],
#                                     'normal': mp.Notes[item['name']]},
#                           'lowest_ap_stages': {'event': mp_event.best_stage[item['name']]['lowest_ap_stages'],
#                                                'normal': mp.best_stage[item['name']]['lowest_ap_stages']},
#                           'balanced_stages': {'event': mp_event.best_stage[item['name']]['balanced_stages'],
#                                               'normal': mp.best_stage[item['name']]['balanced_stages']},
#                           'drop_rate_first_stages': {'event': mp_event.best_stage[item['name']]['drop_rate_first_stages'],
#                                                      'normal': mp.best_stage[item['name']]['drop_rate_first_stages']},
#                           'last_updated': update_time
#                          }
#                 },upsert=InjectNew)
#         else:
#             collection.update_one({'_id': item['_id']},
#                 {'$set': {'credit_store_value': {'event': '%.3f'%(100*mp_event.creditEffect[item['name']]),
#                                                  'normal': '%.3f'%(100*mp.creditEffect[item['name']])},
#                           'Notes': {'event': mp_event.Notes[item['name']],
#                                     'normal': mp.Notes[item['name']]},
#                           'lowest_ap_stages': {'event': [],
#                                                'normal': []},
#                           'balanced_stages': {'event': [],
#                                                'normal': []},
#                           'drop_rate_first_stages': {'event': [],
#                                                'normal': []},
#                           'last_updated': update_time}
#                 },upsert=InjectNew)
#     if 'green_ticket_value' in item:
#         if item['name'] in mp.best_stage:
#             collection.update_one({'_id': item['_id']},
#                 {'$set': {'green_ticket_value': {'event': '%.3f'%(mp_event.greenTickets[item['name']]),
#                                                  'normal': '%.3f'%(mp.greenTickets[item['name']])},
#                           'Notes': {'event': mp_event.Notes[item['name']],
#                                     'normal': mp.Notes[item['name']]},
#                           'lowest_ap_stages': {'event': mp_event.best_stage[item['name']]['lowest_ap_stages'],
#                                                'normal': mp.best_stage[item['name']]['lowest_ap_stages']},
#                           'balanced_stages': {'event': mp_event.best_stage[item['name']]['balanced_stages'],
#                                               'normal': mp.best_stage[item['name']]['balanced_stages']},
#                           'drop_rate_first_stages': {'event': mp_event.best_stage[item['name']]['drop_rate_first_stages'],
#                                                      'normal': mp.best_stage[item['name']]['drop_rate_first_stages']},
#                           'last_updated': update_time}})
#         else:
#             collection.update_one({'_id': item['_id']},
#                 {'$set': {'green_ticket_value': {'event': '%.3f'%(mp_event.greenTickets[item['name']]),
#                                                  'normal': '%.3f'%(mp.greenTickets[item['name']])},
#                           'Notes': {'event': mp_event.Notes[item['name']],
#                                     'normal': mp.Notes[item['name']]},
#                           'lowest_ap_stages': {'event': [],
#                                                'normal': []},
#                           'balanced_stages': {'event': [],
#                                                'normal': []},
#                           'drop_rate_first_stages': {'event': [],
#                                                'normal': []},
#                           'last_updated': update_time}},upsert=InjectNew)
#     if 'golden_ticket_value' in item:
#         collection.update_one({'_id': item['_id']},
#                 {'$set': {'golden_ticket_value': {'event': '%.3f'%(mp_event.yellowTickets[item['name']]),
#                                                  'normal': '%.3f'%(mp.yellowTickets[item['name']])},
#                           'Notes': {'event': mp_event.Notes[item['name']],
#                                     'normal': mp.Notes[item['name']]},
#                           'last_updated': update_time}},upsert=InjectNew)
#
# # Write in the db, with considering income from base
# for item in collection_exp.find():
#     x = item['name']
#     print('已更新%s\t' % x, end='\t')
#
#     collection_exp.update_one({'_id': item['_id']},
#                           {'$set': {'contingency_store_value': {'infinite': '%.3f'%mp_expFromBase.HeYueDict[x] if x in mp_expFromBase.HeYueDict else '0.0',
#                                                                 'finite': '%.3f'%mp_expFromBase.HYODict[x] if x in mp_expFromBase.HYODict else '0.0'}}
#             },upsert=InjectNew)
#     if item['name'] in mp_expFromBase.orangeTickets:
#         collection_exp.update_one({'_id': item['_id']},
#                   {'$set': {'orange_store_value': {'event': '%.3f'%mp_event_base.orangeTickets[item['name']],
#                                                    'normal': '%.3f'%mp_expFromBase.orangeTickets[item['name']]},
#                             'orange_note': {'event': mp_event_base.orangeNotes[item['name']],
#                                             'normal': mp_expFromBase.orangeNotes[item['name']]}
#                            }
#                   },upsert=InjectNew)
#     if 'credit_store_value' in item:
#         if item['name'] in mp_expFromBase.best_stage:
#             collection_exp.update_one({'_id': item['_id']},
#                 {'$set': {'credit_store_value': {'event': '%.3f'%(100*mp_event_base.creditEffect[item['name']]),
#                                                  'normal': '%.3f'%(100*mp_expFromBase.creditEffect[item['name']])},
#                           'Notes': {'event': mp_event_base.Notes[item['name']],
#                                     'normal': mp_expFromBase.Notes[item['name']]},
#                           'lowest_ap_stages': {'event': mp_event_base.best_stage[item['name']]['lowest_ap_stages'],
#                                                'normal': mp_expFromBase.best_stage[item['name']]['lowest_ap_stages']},
#                           'balanced_stages': {'event': mp_event_base.best_stage[item['name']]['balanced_stages'],
#                                               'normal': mp_expFromBase.best_stage[item['name']]['balanced_stages']},
#                           'drop_rate_first_stages': {'event': mp_event_base.best_stage[item['name']]['drop_rate_first_stages'],
#                                                      'normal': mp_expFromBase.best_stage[item['name']]['drop_rate_first_stages']},
#                           'last_updated': update_time
#                          }
#                 },upsert=InjectNew)
#         else:
#             collection_exp.update_one({'_id': item['_id']},
#                 {'$set': {'credit_store_value': {'event': '%.3f'%(100*mp_event_base.creditEffect[item['name']]),
#                                                  'normal': '%.3f'%(100*mp_expFromBase.creditEffect[item['name']])},
#                           'Notes': {'event': mp_event_base.Notes[item['name']],
#                                     'normal': mp_expFromBase.Notes[item['name']]},
#                           'lowest_ap_stages': {'event': [],
#                                                'normal': []},
#                           'balanced_stages': {'event': [],
#                                                'normal': []},
#                           'drop_rate_first_stages': {'event': [],
#                                                'normal': []},
#                           'last_updated': update_time}
#                 })
#     if 'green_ticket_value' in item:
#         if item['name'] in mp_expFromBase.best_stage:
#             collection_exp.update_one({'_id': item['_id']},
#                 {'$set': {'green_ticket_value': {'event': '%.3f'%(mp_event_base.greenTickets[item['name']]),
#                                                  'normal': '%.3f'%(mp_expFromBase.greenTickets[item['name']])},
#                           'Notes': {'event': mp_event_base.Notes[item['name']],
#                                     'normal': mp_expFromBase.Notes[item['name']]},
#                           'lowest_ap_stages': {'event': mp_event_base.best_stage[item['name']]['lowest_ap_stages'],
#                                                'normal': mp_expFromBase.best_stage[item['name']]['lowest_ap_stages']},
#                           'balanced_stages': {'event': mp_event_base.best_stage[item['name']]['balanced_stages'],
#                                               'normal': mp_expFromBase.best_stage[item['name']]['balanced_stages']},
#                           'drop_rate_first_stages': {'event': mp_event_base.best_stage[item['name']]['drop_rate_first_stages'],
#                                                      'normal': mp_expFromBase.best_stage[item['name']]['drop_rate_first_stages']},
#                           'last_updated': update_time}},upsert=InjectNew)
#         else:
#             collection_exp.update_one({'_id': item['_id']},
#                 {'$set': {'green_ticket_value': {'event': '%.3f'%(mp_event_base.greenTickets[item['name']]),
#                                                  'normal': '%.3f'%(mp_expFromBase.greenTickets[item['name']])},
#                           'Notes': {'event': mp_event_base.Notes[item['name']],
#                                     'normal': mp_expFromBase.Notes[item['name']]},
#                           'lowest_ap_stages': {'event': [],
#                                                'normal': []},
#                           'balanced_stages': {'event': [],
#                                                'normal': []},
#                           'drop_rate_first_stages': {'event': [],
#                                                'normal': []},
#                           'last_updated': update_time}},upsert=InjectNew)
#     if 'golden_ticket_value' in item:
#         collection_exp.update_one({'_id': item['_id']},
#                 {'$set': {'golden_ticket_value': {'event': '%.3f'%(mp_event_base.yellowTickets[item['name']]),
#                                                  'normal': '%.3f'%(mp_expFromBase.yellowTickets[item['name']])},
#                           'Notes': {'event': mp_event_base.Notes[item['name']],
#                                     'normal': mp_expFromBase.Notes[item['name']]},
#                           'last_updated': update_time}},upsert=InjectNew)
#
# embed = DiscordEmbed(title='Scripts ran', description='running ok without errors', color=242424)
# webhook.add_embed(embed)
# response = webhook.execute()
print('\nCN服更新完成.')
