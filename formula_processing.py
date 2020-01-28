# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 19:22:26 2019

@author: sqr_p
"""

formula = json.load(open('data/formula_bak.json', 'r', encoding='utf8'))

Level4Extra = [{'count': 1, 'id': '31013', 'name': '凝胶', 'rarity': 2, 'weight': 36},
          {'count': 1, 'id': '31023', 'name': '炽合金', 'rarity': 2, 'weight': 40}]
for x in formula:
    if x['id'][-1] == '4':
        x['extraOutcome'] += Level4Extra
        x['totalWeight'] += 36+40

Level5Extra = [{'count': 1, 'id': '31014', 'name': '聚合凝胶', 'rarity': 3, 'weight': 72},
          {'count': 1, 'id': '31024', 'name': '炽合金块', 'rarity': 3, 'weight': 63}]
for x in formula:
    if x['id'][-1] == '5':
        x['extraOutcome'] += Level5Extra
        x['totalWeight'] += 72+63
        s = x

ChiHeJinKuai = {'costs': [{'count': 1, 'id': '30063', 'name': '全新装置', 'rarity': 2},
  {'count': 1, 'id': '30093', 'name': '研磨石', 'rarity': 2},
  {'count': 1, 'id': '31023', 'name': '炽合金', 'rarity': 2}],
 'extraOutcome': [{'count': 1,
   'id': '30013',
   'name': '固源岩组',
   'rarity': 2,
   'weight': 60},
  {'count': 1, 'id': '30023', 'name': '糖组', 'rarity': 2, 'weight': 50},
  {'count': 1, 'id': '30033', 'name': '聚酸酯组', 'rarity': 2, 'weight': 50},
  {'count': 1, 'id': '30043', 'name': '异铁组', 'rarity': 2, 'weight': 40},
  {'count': 1, 'id': '30053', 'name': '酮凝集组', 'rarity': 2, 'weight': 40},
  {'count': 1, 'id': '30063', 'name': '全新装置', 'rarity': 2, 'weight': 30},
  {'count': 1, 'id': '30073', 'name': '扭转醇', 'rarity': 2, 'weight': 45},
  {'count': 1, 'id': '30083', 'name': '轻锰矿', 'rarity': 2, 'weight': 40},
  {'count': 1, 'id': '30093', 'name': '研磨石', 'rarity': 2, 'weight': 36},
  {'count': 1, 'id': '30103', 'name': 'RMA70-12', 'rarity': 2, 'weight': 30},
  {'count': 1, 'id': '31013', 'name': '凝胶', 'rarity': 2, 'weight': 36},
  {'count': 1, 'id': '31023', 'name': '炽合金', 'rarity': 2, 'weight': 40}],
 'goldCost': 300,
 'id': '31024',
 'name': '炽合金块',
 'totalWeight': 497}

JuHeNingJiao = {'costs': [{'count': 1, 'id': '30043', 'name': '异铁组', 'rarity': 2},
  {'count': 1, 'id': '31013', 'name': '凝胶', 'rarity': 2},
  {'count': 1, 'id': '31023', 'name': '炽合金', 'rarity': 2}],
 'extraOutcome': [{'count': 1,
   'id': '30013',
   'name': '固源岩组',
   'rarity': 2,
   'weight': 60},
  {'count': 1, 'id': '30023', 'name': '糖组', 'rarity': 2, 'weight': 50},
  {'count': 1, 'id': '30033', 'name': '聚酸酯组', 'rarity': 2, 'weight': 50},
  {'count': 1, 'id': '30043', 'name': '异铁组', 'rarity': 2, 'weight': 40},
  {'count': 1, 'id': '30053', 'name': '酮凝集组', 'rarity': 2, 'weight': 40},
  {'count': 1, 'id': '30063', 'name': '全新装置', 'rarity': 2, 'weight': 30},
  {'count': 1, 'id': '30073', 'name': '扭转醇', 'rarity': 2, 'weight': 45},
  {'count': 1, 'id': '30083', 'name': '轻锰矿', 'rarity': 2, 'weight': 40},
  {'count': 1, 'id': '30093', 'name': '研磨石', 'rarity': 2, 'weight': 36},
  {'count': 1, 'id': '30103', 'name': 'RMA70-12', 'rarity': 2, 'weight': 30},
  {'count': 1, 'id': '31013', 'name': '凝胶', 'rarity': 2, 'weight': 36},
  {'count': 1, 'id': '31023', 'name': '炽合金', 'rarity': 2, 'weight': 40}],
 'goldCost': 300,
 'id': '31014',
 'name': '聚合凝胶',
 'totalWeight': 497}

formula += [ChiHeJinKuai, JuHeNingJiao]
with open('data/formula.json', 'w', encoding='gbk') as outfile:
    json.dump(formula, outfile, indent=1, ensure_ascii=False)

