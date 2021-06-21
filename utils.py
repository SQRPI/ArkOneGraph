# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 22:32:11 2019

@author: sqr_p
@modified: strontium
"""
import codecs
import pymongo
import json
# Aggregation
def aggregation(collection, required_dct, heroine_name):
    # Initialization
    figureCount = {
        '1/2-Star': 0,
        '3-Star': 0,
        '4-Star': 0,
        '5-Star': 0,
        '6-Star': 0
    }
    bookCount = {
        '技巧概要·卷1': 0,
        '技巧概要·卷2': 0,
        '技巧概要·卷3': 0
    }

    # Lookup Tables
    skillLvlCost = ['1to2', '2to3', '3to4', '4to5', '5to6', '6to7',
                    'S1M1', 'S1M2', 'S1M3', 'S2M1', 'S2M2', 'S2M3',
                    'S3M1', 'S3M2', 'S3M3']
    classesList = {'MEDIC': '医疗', 'WARRIOR': '近卫', 'SPECIAL': '特种', 'TANK': '重装', 'PIONEER': '先锋', 'SNIPER': '狙击',
                   'CASTER': '术师',
                   'SUPPORT': '辅助'}
    for item in collection.find():
        if item['rarity']<2: #1,2*
            figureCount['1/2-Star'] +=1

        elif item['rarity'] == 2: #3*
            figureCount['3-Star'] += 1
            for i in range(0,6):
                for k in item[skillLvlCost[i]]:
                    if k['id'] == '3301':
                        bookCount['技巧概要·卷1'] += k['count']
                    elif k['id'] == '3302':
                        bookCount['技巧概要·卷2'] += k['count']
                    elif k['id'] == '3303':
                        bookCount['技巧概要·卷3'] += k['count']
                    elif k['id'] in Item_table.keys():
                        required_dct[Item_table[k['id']]] += k['count']

        elif item['rarity'] == 3: #4*
            figureCount['4-Star'] += 1
            profession = classesList[item['profession']]
            required_dct[profession+'芯片']+=3
            required_dct[profession + '双芯片'] += 5
            for i in range(0,12):
                for k in item[skillLvlCost[i]]:
                    if k['id'] == '3301':
                        bookCount['技巧概要·卷1'] += k['count']
                    elif k['id'] == '3302':
                        bookCount['技巧概要·卷2'] += k['count']
                    elif k['id'] == '3303':
                        bookCount['技巧概要·卷3'] += k['count']
                    elif k['id'] in Item_table.keys():
                        required_dct[Item_table[k['id']]] += k['count']

        elif item['rarity'] == 4: #5*
            figureCount['5-Star'] += 1
            profession = classesList[item['profession']]
            required_dct[profession + '芯片'] += 4
            required_dct[profession + '芯片组'] += 3
            if item['_id'] != heroine_name:
                for i in range(0, 12):
                    for k in item[skillLvlCost[i]]:
                        if k['id'] == '3301':
                            bookCount['技巧概要·卷1'] += k['count']
                        elif k['id'] == '3302':
                            bookCount['技巧概要·卷2'] += k['count']
                        elif k['id'] == '3303':
                            bookCount['技巧概要·卷3'] += k['count']
                        elif k['id'] in Item_table.keys():
                            required_dct[Item_table[k['id']]] += k['count']
            else:
                for i in range(0, 15):
                    for k in item[skillLvlCost[i]]:
                        if k['id'] == '3301':
                            bookCount['技巧概要·卷1'] += k['count']
                        elif k['id'] == '3302':
                            bookCount['技巧概要·卷2'] += k['count']
                        elif k['id'] == '3303':
                            bookCount['技巧概要·卷3'] += k['count']
                        elif k['id'] in Item_table.keys():
                            required_dct[Item_table[k['id']]] += k['count']

        else: #6*
            figureCount['6-Star'] +=1
            profession = classesList[item['profession']]
            required_dct[profession + '芯片'] += 5
            required_dct[profession + '芯片组'] += 4
            for i in range(0, 15):
                for k in item[skillLvlCost[i]]:
                    if k['id'] == '3301':
                        bookCount['技巧概要·卷1'] += k['count']
                    elif k['id'] == '3302':
                        bookCount['技巧概要·卷2'] += k['count']
                    elif k['id'] == '3303':
                        bookCount['技巧概要·卷3'] += k['count']
                    elif k['id'] in Item_table.keys():
                        required_dct[Item_table[k['id']]] += k['count']
    exp_required = {
        '1/2-Star': 9800,
        '3-Star': 115400,
        '4-Star': 484000,
        '5-Star': 734400,
        '6-Star': 1111400
    }
    gold_required = {
        '1/2-Star': 5323,
        '3-Star': 104040,
        '4-Star': 482003,
        '5-Star': 819325,
        '6-Star': 1334769
    }
    required_dct.update({
        '经验': sum(v * exp_required[k] for k, v in figureCount.items()),
        '龙门币': sum(v * gold_required[k] for k, v in figureCount.items()),
        '家具零件': 10000,
        '采购凭证': 1000
    })
    # required_dct.update({
    #                        '经验': 0,
    #                        '龙门币': 0,
    #                        '家具零件': 0
    #                    })
    # required_dct.update({# 更新时间: 2020/4/23 傀影池
    #                         '技巧概要·卷1': 818,
    #                         '技巧概要·卷2': 1812,
    #                         '技巧概要·卷3': 5911
    #                     })
    required_dct.update(bookCount)
    required_dct.update({ # 扩大价值，否则橙票商店会崩溃
                       '凝胶': 261,
                       '聚合凝胶': 384,
                       '炽合金': 248,
                       '炽合金块': 366
                   })
    if heroine_name == "阿米娅":
        required_dct.update({ # 扩大价值，否则橙票商店会崩溃
                          '晶体电路':   100,
                          '晶体元件':   100,
                          '晶体电子单元': 100
                       })

    return required_dct


server = open('data/server.txt', 'r').readline().strip()
dbclient = pymongo.MongoClient(server)
db = dbclient['ArknightsGamedata']
collectionCN = db['CharactersCN']
collectionENJPKR = db['CharactersENJPKR']
collectionTW = db['CharactersTW']

Price = dict()
with open('data/price.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        Price[name] = int(value)

Credit = dict()
with open('data/creditPrice.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        Credit[name] = float(value)

HeYue_1 = dict()
with open('data/HeYue-1.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HeYue_1[name] = float(eval(value))

HYO_1 = dict()
with open('data/HeYueOrd-1.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HYO_1[name] = float(eval(value))

HeYue0 = dict()
with open('data/HeYue0.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HeYue0[name] = float(eval(value))

HYO0 = dict()
with open('data/HeYueOrd0.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HYO0[name] = float(eval(value))

HeYue1 = dict()
with open('data/HeYue1.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HeYue1[name] = float(eval(value))

HYO1 = dict()
with open('data/HeYueOrd1.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HYO1[name] = float(eval(value))

HeYue2 = dict()
with open('data/HeYue2.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HeYue2[name] = float(eval(value))

HYO2 = dict()
with open('data/HeYueOrd2.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HYO2[name] = float(eval(value))
        
HeYue3 = dict()
with open('data/HeYue3.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HeYue3[name] = float(eval(value))

HYO3 = dict()
with open('data/HeYueOrd3.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HYO3[name] = float(eval(value))

HeYue4 = dict()
with open('data/HeYue4.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HeYue4[name] = float(eval(value))

HYO4 = dict()
with open('data/HeYueOrd4.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HYO4[name] = float(eval(value))

HeYue5 = dict()
with open('data/HeYue5.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HeYue5[name] = float(eval(value))

HYO5 = dict()
with open('data/HeYueOrd5.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HYO5[name] = float(eval(value))

CCStores = [HeYue_1, HYO_1, HeYue0, HYO0, HeYue1, HYO1, HeYue2, HYO2,HeYue3, HYO3,HeYue4, HYO4,HeYue5, HYO5]

Orange = dict()
with open('data/orange.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        name, value = line.split()
        Orange[name] = float(eval(value))

Purple = dict()
with open('data/purple.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        name, value = line.split()
        Purple[name] = float(eval(value))

with codecs.open('data/materialIO.txt', 'r', 'utf-8') as f:
    material = eval(f.readline())
    required_dctCN = {x['name']: 0 for x in material}
    required_dctENJPKR = {x['name']: 0 for x in material}
    required_dctTW = {x['name']: 0 for x in material}
    owned_dct = {x['name']: x['have'] for x in material}

with open('data/chips.csv', 'r', encoding='utf-8') as f:
    class_name = f.readline().strip().split(',')[1:]
    for _ in range(3):
        content = f.readline().strip().split(',')
        item_name, num = content[0], [int(x) for x in content[1:]]
        for i in range(8):
            required_dctCN.update({class_name[i] + item_name: 0})
            required_dctENJPKR.update({class_name[i] + item_name: 0})
            required_dctTW.update({class_name[i] + item_name: 0})

Item_table = dict()
with open('data/item_table.json', encoding='UTF-8') as rawFile:
    itemTable = json.load(rawFile)
    materialTable = itemTable['items']
    for item in materialTable.keys():
        if materialTable[item]['itemType'] == 'MATERIAL' and item.isdigit() and len(item)==5 and item !='32001':
            Item_table.update({materialTable[item]['itemId']: materialTable[item]['name']})

# 当前干员数量
# figureCount = {# 更新时间: 2020/06/02 石棉/月禾池
#                '1/2-Star': 7,
#                '3-Star': 17,
#                '4-Star': 37,
#                '5-Star': 52,
#                '6-Star': 22
#               }


# Aggregation on number of characters in DB for all 3 servers
# It is AAAAAAAAAAAAAUUUUUUUTTTTTOOOOOOMMATIC!
# aggregation(collectionCN,required_dctCN,"阿米娅")
# aggregation(collectionENJPKR,required_dctENJPKR,"Amiya")
# aggregation(collectionTW,required_dctTW,"阿米婭")

owned_dct.update({'经验': 0, '龙门币': 0, '技巧概要·卷3': 0,
                  '技巧概要·卷2': 0, '技巧概要·卷1': 0})

凝胶_group = {'固源岩组':[4/3, 60/171*4],
            '扭转醇':[3/3, 45/171*4],
            '全新装置':[2/3, 30/171*4]}

凝胶_update = {
            '4-10': '全新装置',
            '4-4': '扭转醇',
            '4-7': '',
            '5-5': '',
            '4-6': '固源岩组',
            '4-1': '',
            '4-3': ''
        }

炽合金_group = {'糖组':[5/13*3, 5/17*4],
                 '轻锰矿':[4/13*3, 4/17*4],
                 '异铁组':[4/13*3, 4/17*4]}

炽合金_update = {
            '5-6': '轻锰矿',
            'S4-7': '',
            'S4-3': '',
            'S4-9': '',
            'S4-1': '异铁组',
            '4-2': '糖组',
            'S4-4': '',
            'S4-6': ''
        }

