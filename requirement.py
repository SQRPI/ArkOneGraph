# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 18:38:00 2019

@author: sqr_p
"""

req = [{"name":"D32钢","need":202,"have":0},{"name":"双极纳米片","need":222,"have":0},{"name":"聚合剂","need":204,"have":0},{"name":"RMA70-24","need":236,"have":0},{"name":"RMA70-12","need":175,"have":0},{"name":"五水研磨石","need":289,"have":0},{"name":"研磨石","need":204,"have":0},{"name":"三水锰矿","need":236,"have":0},{"name":"轻锰矿","need":220,"have":0},{"name":"白马醇","need":283,"have":0},{"name":"扭转醇","need":293,"have":0},{"name":"改量装置","need":161,"have":0},{"name":"全新装置","need":178,"have":0},{"name":"装置","need":114,"have":0},{"name":"破损装置","need":46,"have":0},{"name":"酮阵列","need":207,"have":0},{"name":"酮凝集组","need":298,"have":0},{"name":"酮凝集","need":146,"have":0},{"name":"双酮","need":51,"have":0},{"name":"异铁块","need":198,"have":0},{"name":"异铁组","need":208,"have":0},{"name":"异铁","need":153,"have":0},{"name":"异铁碎片","need":65,"have":0},{"name":"聚酸酯块","need":246,"have":0},{"name":"聚酸酯组","need":221,"have":0},{"name":"聚酸酯","need":181,"have":0},{"name":"酯原料","need":83,"have":0},{"name":"糖聚块","need":269,"have":0},{"name":"糖组","need":249,"have":0},{"name":"糖","need":183,"have":0},{"name":"代糖","need":76,"have":0},{"name":"提纯源岩","need":287,"have":0},{"name":"固源岩组","need":298,"have":0},{"name":"固源岩","need":240,"have":0},{"name":"源岩","need":113,"have":0}]
with open('required.txt', 'w', encoding='utf8') as f:
    for item in req:
        f.write('%s %s\n'% (item['name'], item['need']))
