# -*- coding: utf-8 -*-
import pymongo
import json
server = open('data/server.txt', 'r').readline().strip()
dbclient = pymongo.MongoClient(server)
db = dbclient['ArknightsGamedata']

collection = db['CharactersCN']



with open('data/character_tableCN.json',encoding='UTF-8') as rawFile:
    characterTableJSON = json.load(rawFile)

    for key in characterTableJSON.keys():
        if 'token' in key:
            continue
        item=characterTableJSON[key]
        name = item['name']
        rarity = item['rarity']
        profession = item['profession']
        if profession == "TRAP":
            continue
        if rarity ==2: #3* characters
            phase1Cost = item['phases'][1]['evolveCost']
            skillCost = []
            for i in item['allSkillLvlup']:
                skillCost.append(i['lvlUpCost'])
            print(name)
            collection.update_one({'_id': name}, {'$set': {'rarity': rarity,
                                                           'profession': profession,
                                                           '1to2': skillCost[0], '2to3': skillCost[1], '3to4': skillCost[2],
                                                           '4to5': skillCost[3],
                                                           '5to6': skillCost[4], '6to7': skillCost[5]
                                                           }
                                                  }, upsert=True)
        elif rarity ==3 or rarity == 4: #4 and 5* characters
            phase1Cost = item['phases'][1]['evolveCost']
            phase2Cost = item['phases'][2]['evolveCost']
            skillCost = []
            for i in item['allSkillLvlup']:
                skillCost.append(i['lvlUpCost'])
            for i in item['skills']:
                for j in i['levelUpCostCond']:
                    skillCost.append(j['levelUpCost'])
            print(name)
            if name =="阿米娅":
                collection.update_one({'_id': name}, {'$set': {'rarity': rarity,
                                                               'profession': profession, 'phase1Cost': phase1Cost,
                                                               'phase2Cost': phase2Cost,
                                                               '1to2': skillCost[0], '2to3': skillCost[1],
                                                               '3to4': skillCost[2],
                                                               '4to5': skillCost[3],
                                                               '5to6': skillCost[4], '6to7': skillCost[5],
                                                               'S1M1': skillCost[6],
                                                               'S1M2': skillCost[7], 'S1M3': skillCost[8],
                                                               'S2M1': skillCost[9],
                                                               'S2M2': skillCost[10], 'S2M3': skillCost[11],
                                                               'S3M1': skillCost[12],
                                                               'S3M2': skillCost[13], 'S3M3': skillCost[14]
                                                               }
                                                      }, upsert=True)
            else:
                collection.update_one({'_id': name}, {'$set': {'rarity': rarity,
                                                           'profession': profession, 'phase1Cost': phase1Cost,
                                                           'phase2Cost': phase2Cost,
                                                           '1to2': skillCost[0], '2to3': skillCost[1], '3to4': skillCost[2],
                                                           '4to5': skillCost[3],
                                                           '5to6': skillCost[4], '6to7': skillCost[5], 'S1M1': skillCost[6],
                                                           'S1M2':skillCost[7], 'S1M3': skillCost[8], 'S2M1': skillCost[9],
                                                           'S2M2': skillCost[10],'S2M3': skillCost[11]
                                                           }
                                                  }, upsert=True)
        elif rarity ==5: #4,5, and 6* characters
            phase1Cost = item['phases'][1]['evolveCost']
            phase2Cost = item['phases'][2]['evolveCost']
            skillCost = []
            for i in item['allSkillLvlup']:
                skillCost.append(i['lvlUpCost'])
            for i in item['skills']:
                for j in i['levelUpCostCond']:
                    skillCost.append(j['levelUpCost'])
            collection.update_one({'_id': name}, {'$set': {'rarity': rarity,
                                                           'profession': profession, 'phase1Cost': phase1Cost,
                                                           'phase2Cost': phase2Cost,
                                                           '1to2': skillCost[0], '2to3': skillCost[1], '3to4': skillCost[2],
                                                           '4to5': skillCost[3],
                                                           '5to6': skillCost[4], '6to7': skillCost[5], 'S1M1': skillCost[6],
                                                           'S1M2':skillCost[7], 'S1M3': skillCost[8], 'S2M1': skillCost[9],
                                                           'S2M2': skillCost[10],'S2M3': skillCost[11],'S3M1': skillCost[12],
                                                           'S3M2': skillCost[13],'S3M3': skillCost[14]
                                                           }
                                                  }, upsert=True)
        else: #1,2* characters
            collection.update_one({'_id': name}, {'$set': {'rarity': rarity,
                                                           'profession': profession}
                                                  }, upsert=True)

    print('\nDone for CN server.')
