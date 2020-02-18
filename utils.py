# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 22:32:11 2019

@author: sqr_p
"""
import codecs

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

HeYue = dict()
with open('data/HeYue.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HeYue[name] = float(value)

HYO = dict()
with open('data/HeYueOrd.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
        name, value = line.split()
        HYO[name] = float(value)

with codecs.open('data/materialIO.txt', 'r', 'utf-8') as f:
    material = eval(f.readline())
    required_dct = {x['name']: x['need'] for x in material}
    owned_dct = {x['name']: x['have'] for x in material}

#with open('data/chips.csv', 'r', encoding='utf-8') as f:
#    class_name = f.readline().strip().split(',')[1:]
#    for _ in range(3):
#        content = f.readline().strip().split(',')
#        item_name, num = content[0], [int(x) for x in content[1:]]
#        for i in range(8):
#            required_dct.update({class_name[i] + item_name: num[i]})
#

# 当前干员数量
figureCount = {# 更新时间: 2020/1/18
               '1/2-Star': 7,
               '3-Star': 17,
               '4-Star': 32+1,
               '5-Star': 43+1+1,
               '6-Star': 16+1+2
              }
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
                        '经验': sum(v*exp_required[k] for k, v in figureCount.items()),
                        '龙门币': sum(v*gold_required[k] for k, v in figureCount.items()),
                        '家具零件': 10000,
                        '采购凭证': 1000
                    })
#required_dct.update({
#                        '经验': 0,
#                        '龙门币': 0,
#                        '家具零件': 0
#                    })
required_dct.update({# 更新时间: 2020/1/18
                        '技巧概要·卷1': 732,
                        '技巧概要·卷2': 1614,
                        '技巧概要·卷3': 5220
                    })
required_dct.update({ # 随便写的, 写几百就行
                        '凝胶': 229,
                        '聚合凝胶': 314,
                        '炽合金': 223,
                        '炽合金块': 335
                    })
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

