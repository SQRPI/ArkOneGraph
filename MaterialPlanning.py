import numpy as np
import urllib.request, json, time, os, copy, sys
from scipy.optimize import linprog
from utils import Price, Credit,  凝胶_group, 凝胶_update, 炽合金_group, 炽合金_update, Orange, CCStores, Purple
from collections import defaultdict as ddict
import pandas as pd

global penguin_url
penguin_url = 'https://penguin-stats.io/PenguinStats/api/'

class MaterialPlanning(object):

    def __init__(self,
                 filter_freq=10,
                 filter_stages=[],
                 url_stats='v2/result/matrix?show_stage_details=true&show_item_details=true',
                 url_rules='formula',
                 path_stats='data/matrix.json',
                 path_rules='data/formula.json',
                 path_items='data/items.json',
                 path_stages='data/stages.json',
                 update=False, 
                 banned_stages={},
#                 expValue=30,
                 ConvertionDR=0.18,
                 printSetting='1111111111',
                 costLimit=135,
                 costType='stone',
                 base_exp=0,
                 base_gold=0,
                 base_MTL_GOLD3=0,
                 is_supply_lt_60=True,
                 stone_per_day=0,
                 display_main_only=True,
                 SuiGuoHuaDeng=False,
                 ExpFromBase=False,
                 CCSeason=1,
                 url_stages='v2/stages',
                 url_items ='v2/items'):
        """
        Object initialization.
        Args:
            filter_freq: int or None. The lowest frequence that we consider.
                No filter will be applied if None.
            url_stats: string. url to the dropping rate stats data.
            url_rules: string. url to the composing rules data.
            path_stats: string. local path to the dropping rate stats data.
            path_rules: string. local path to the composing rules data.
        """
        try:
            material_probs, self.convertion_rules, self.item_list, self.stage_list = load_data(path_stats, path_rules, path_items, path_stages)
        except:
            print('获取本地文件失败...', end=' ')
            material_probs, self.convertion_rules, self.item_list, self.stage_list =\
            request_data(penguin_url+url_stats, penguin_url+url_rules, penguin_url+url_items,
                         penguin_url+url_stages, path_stats, path_rules, path_items, path_stages)
            print('done.')
        if update:
            print('强制更新...', end=' ')
            material_probs, self.convertion_rules, self.item_list, self.stage_list =\
            request_data(penguin_url+url_stats, penguin_url+url_rules, penguin_url+url_items,
                         penguin_url+url_stages, path_stats, path_rules, path_items, path_stages)
            print('done.')


        self.exp_factor = 1

        self.公招出四星的概率 = 0.186
        self.costLimit = costLimit #理智上限
#        self.convertion_rules = convertion_rules
        self.material_probs = material_probs
        self.banned_stages = banned_stages
        self.costType = costType
        self.display_main_only = display_main_only
        self.SuiGuoHuaDeng = SuiGuoHuaDeng
        self.stage_times = ddict(int)
        self.Notes = dict()
        self.best_stage = dict()
        self.ExpFromBase = ExpFromBase

        self.base_exp = base_exp
        self.base_gold = base_gold
        self.base_MTL_GOLD3 = base_MTL_GOLD3
        self.everyday_cost = (200-25*5)/7 + 240 + 60 * is_supply_lt_60 + stone_per_day*self.costLimit

        self.ccseason = CCSeason
        filtered_probs = []
        excluded_stages = set()
        for dct in material_probs['matrix']:
            if dct['itemId'] == "4006":  # 打包 :(
                continue
            item, stage, times = self.item_list[dct['itemId']], self.stage_list[dct['stageId']]['code'], int(dct['times'])
            if item in filter_stages: continue
            if times > self.stage_times[stage] or self.stage_times[stage] == 0 and stage not in filter_stages:
                self.stage_times[stage] = times
            if times >= filter_freq and stage not in filter_stages:
                filtered_probs.append(dct)
            elif stage not in excluded_stages:
                print('%8s的 %s 未加入统计, 样本数%d'%(stage, item, times))
                excluded_stages.add(stage)
        material_probs['matrix'] = filtered_probs

        self.ConvertionDR = ConvertionDR
        self._pre_processing(material_probs)
        self._set_lp_parameters()
        assert len(printSetting)==12, 'printSetting 长度应为10'
        assert printSetting.count('1') + printSetting.count('0') == 12, 'printSetting 中只能含有0或1'
        self.printSetting = [int(x) for x in printSetting]


    def _pre_processing(self, material_probs):
        """
        Compute costs, convertion rules and items probabilities from requested dictionaries.
        Args:
            material_probs: List of dictionaries recording the dropping info per stage per item.
                Keys of instances: ["itemID", "times", "itemName", "quantity", "apCost", "stageCode", "stageID"].
            convertion_rules: List of dictionaries recording the rules of composing.
                Keys of instances: ["id", "name", "level", "source", "madeof"].
        """
        # To count items and stages.
        additional_items = {'30135': u'D32钢', '30125': u'双极纳米片',
                            '30115': u'聚合剂', '00010':'经验', '4001':'龙门币',
                            '31014':'聚合凝胶', '31024':'炽合金块', '31013':'凝胶',
                            '31023':'炽合金',
                            '3303':'技巧概要·卷3', '3302':'技巧概要·卷2', '3301':'技巧概要·卷1',
                            '00030':'家具零件', '3003': '赤金',
                            '3211': '先锋芯片', '3212': '先锋芯片组', '3213': '先锋双芯片',
                            '3221': '近卫芯片', '3222': '近卫芯片组', '3223': '近卫双芯片',
                            '3231': '重装芯片', '3232': '重装芯片组', '3233': '重装双芯片',
                            '3241': '狙击芯片', '3242': '狙击芯片组', '3243': '狙击双芯片',
                            '3251': '术师芯片', '3252': '术师芯片组', '3253': '术师双芯片',
                            '3261': '医疗芯片', '3262': '医疗芯片组', '3263': '医疗双芯片',
                            '3271': '辅助芯片', '3272': '辅助芯片组', '3273': '辅助双芯片',
                            '3281': '特种芯片', '3282': '特种芯片组', '3283': '特种双芯片',
                            '4006': '采购凭证', '7003': '寻访凭证', '32001': '芯片助剂',
                            '7001': '招聘许可',
                            '2004': '高级作战记录', '2003': '中级作战记录', '2002': '初级作战记录', '2001': '基础作战记录',
                            '3112': '碳', '3113': '碳素', '3114': '碳素组',
                            '4003': '合成玉',
                            '31033': '晶体元件', '31034': '晶体电路', '30145': '晶体电子单元'
                            }
        additional_items = {k: v for v, k in additional_items.items()}
        item_dct = {}
        stage_dct = {}

        for dct in material_probs['matrix']:
            item_dct[self.item_list[dct['itemId']]] = dct['itemId']
            stage_dct[self.stage_list[dct['stageId']]['code']] = dct['stageId']
        item_dct.update(additional_items)
        # To construct mapping from id to item names.
        item_array = []
        item_id_array = []
        for v, k in item_dct.items():
            try:
                float(k)
                item_array.append(v)
                item_id_array.append(k)
            except:
                pass
        self.item_array = np.array(item_array)
        self.item_id_array = np.array(item_id_array)
        self.item_dct_rv = {v:k for k,v in enumerate(item_array)}
        self.item_id_to_name = {self.item_id_array[k]:item for k,item in enumerate(item_array)}
        self.item_name_to_id = {item:self.item_id_array[k] for k,item in enumerate(item_array)}

        # To construct mapping from stage id to stage names and vice versa.
        self.stage_array =[]
        for v, k in stage_dct.items():
            if v not in self.banned_stages:
                self.stage_array.append(v)

        self.stage_dct_rv = {v: k for k, v in enumerate(self.stage_array)}

        # To format dropping records into sparse probability matrix
        self.cost_lst = np.zeros(len(self.stage_array))

        self.update_stage()
        self.stage_array = np.array(self.stage_array)
        self.probs_matrix = np.zeros([len(self.stage_array), len(item_array)])

        for dct in material_probs['matrix']:
            try:
                if dct['itemId'] == 'furni': continue
                item, stage, cost = self.item_id_to_name[dct['itemId']], self.stage_list[dct['stageId']]['code'], int(self.stage_list[dct['stageId']]['cost'])
                self.probs_matrix[self.stage_dct_rv[stage], self.item_dct_rv[item]] = dct['quantity'] / int(dct['times'])

                self.cost_lst[self.stage_dct_rv[stage]] = cost
            except Exception as e:
                print(f'材料{item}\t关卡{stage}({cost}) 添加失败 {e}')

        for k, stage in enumerate(self.stage_array):
            self.probs_matrix[k, self.item_dct_rv['龙门币']] = self.cost_lst[k]*12
        self.update_droprate()

        # To build equavalence relationship from convert_rule_dct.
        self.update_convertion()
        self.convertions_dct = {}
        convertion_matrix = []
        convertion_outc_matrix = []
        convertion_cost_lst = []
        for rule in self.convertion_rules:
            convertion = np.zeros(len(self.item_array))
            convertion[self.item_dct_rv[rule['name']]] = 1

            comp_dct = {comp['name']:comp['count'] for comp in rule['costs']}
            self.convertions_dct[rule['name']] = comp_dct
            for iname in comp_dct:
                convertion[self.item_dct_rv[iname]] -= comp_dct[iname]
            convertion[self.item_dct_rv['龙门币']] -= rule['goldCost']
            convertion_matrix.append(copy.deepcopy(convertion))

            outc_dct = {outc['name']:outc['count'] for outc in rule['extraOutcome']}
            outc_wgh = {outc['name']:outc['weight'] for outc in rule['extraOutcome']}
            weight_sum = float(rule['totalWeight'])
            for iname in outc_dct:
                convertion[self.item_dct_rv[iname]] += outc_dct[iname]*self.ConvertionDR*outc_wgh[iname]/weight_sum
            convertion_outc_matrix.append(convertion)
            convertion_cost_lst.append(0)


        # 处理新材料
        for stage, item in 凝胶_update.items():
            if stage not in self.stage_array:
                continue
            蓝色额外产物原掉率 = np.mean([self.probs_matrix[self.stage_dct_rv[stage]][self.item_dct_rv[x]]*w[0] for x, w in 凝胶_group.items() if x != item])
            蓝色额外产物实际掉率 = self.probs_matrix[self.stage_dct_rv[stage]][self.item_dct_rv['凝胶']]/(36/171*4)
            修正值 = 蓝色额外产物实际掉率 - 蓝色额外产物原掉率
            for item, w in 凝胶_group.items():
                self.probs_matrix[self.stage_dct_rv[stage]][self.item_dct_rv[item]] += 修正值*w[1]

        for stage, item in 炽合金_update.items():
            if stage not in self.stage_array:
                continue
            蓝色额外产物原掉率 = np.mean([self.probs_matrix[self.stage_dct_rv[stage]][self.item_dct_rv[x]]*w[0] for x in 炽合金_group if x != item])
            蓝色额外产物实际掉率 = self.probs_matrix[self.stage_dct_rv[stage]][self.item_dct_rv['炽合金']]/(4/17*4)
            修正值 = 蓝色额外产物实际掉率 - 蓝色额外产物原掉率
            for item, w in 炽合金_group.items():
                self.probs_matrix[self.stage_dct_rv[stage]][self.item_dct_rv[item]] += 修正值*w[1]


        convertions_group = (np.array(convertion_matrix), np.array(convertion_outc_matrix), convertion_cost_lst)
        self.convertion_matrix, self.convertion_outc_matrix, self.convertion_cost_lst = convertions_group

    def _set_lp_parameters(self):
        """
        Object initialization.
        Args:
            convertion_matrix: matrix of shape [n_rules, n_items].
                Each row represent a rule.
            convertion_cost_lst: list. Cost in equal value to the currency spent in convertion.
            probs_matrix: sparse matrix of shape [n_stages, n_items].
                Items per clear (probabilities) at each stage.
            cost_lst: list. Costs per clear at each stage.
        """
        assert len(self.probs_matrix)==len(self.cost_lst)
        assert len(self.convertion_matrix)==len(self.convertion_cost_lst)
        assert self.probs_matrix.shape[1]==self.convertion_matrix.shape[1]

    def update(self,
               filter_freq=20,
               filter_stages=[],
               url_stats='result/matrix?show_stage_details=true&show_item_details=true',
               url_rules='formula',
               path_stats='data/matrix.json',
               path_rules='data/formula.json'):
        """
        To update parameters when probabilities change or new items added.
        Args:
            url_stats: string. url to the dropping rate stats data.
            url_rules: string. url to the composing rules data.
            path_stats: string. local path to the dropping rate stats data.
            path_rules: string. local path to the composing rules data.
        """
        print('Requesting data from web resources (i.e., penguin-stats.io)...', end=' ')
        material_probs, self.convertion_rules = request_data(penguin_url+url_stats, penguin_url+url_rules, path_stats, path_rules)
        print('done.')

        if filter_freq:
            filtered_probs = []
            for dct in material_probs['matrix']:
                if dct['times']>=filter_freq and dct['stage']['code'] not in filter_stages:
                    filtered_probs.append(dct)
            material_probs['matrix'] = filtered_probs
        self._pre_processing(material_probs)
        self._set_lp_parameters()


    def _get_plan_no_prioties(self, demand_lst, outcome=False, gold_demand=True, exp_demand=True):
        """
        To solve linear programming problem without prioties.
        Args:
            demand_lst: list of materials demand. Should include all items (zero if not required).
        Returns:
            strategy: list of required clear times for each stage.
            fun: estimated total cost.
        """
        A_ub = (np.vstack([self.probs_matrix, self.convertion_outc_matrix])
                if outcome else np.vstack([self.probs_matrix, self.convertion_matrix])).T
        if self.costType == 'time':
            timedata = pd.read_csv('data/time.csv')
            for k, v in enumerate(self.stage_array):
                for l, s in enumerate(timedata.stage):
                    if s[1:-1] == v:
                        self.cost_lst[k] = timedata.time[l]
                        break
        self.farm_cost = (self.cost_lst)
        cost = (np.hstack([self.farm_cost, self.convertion_cost_lst]))
        assert np.any(self.farm_cost>=0)

        excp_factor = 1.0
        dual_factor = 1.0

        while excp_factor>1e-7:
            solution = linprog(c=cost,
                               A_ub=-A_ub,
                               b_ub=-np.array(demand_lst)*excp_factor,
                               method='interior-point')
            if solution.status != 4:
                break

            excp_factor /= 10.0

        while dual_factor>1e-7:
            dual_solution = linprog(c=-np.array(demand_lst)*excp_factor*dual_factor,
                                    A_ub=A_ub.T,
                                    b_ub=cost,
                                    method='interior-point')
            if solution.status != 4:
                break

            dual_factor /= 10.0


        return solution, dual_solution, excp_factor

    def get_plan(self, requirement_dct, deposited_dct={},
                 print_output=False, outcome=False, gold_demand=True, exp_demand=True):
        """
        User API. Computing the material plan given requirements and owned items.
        Args:
                requirement_dct: dictionary. Contain only required items with their numbers.
                deposit_dct: dictionary. Contain only owned items with their numbers.
        """
        self.print_output = print_output
        status_dct = {0: 'Optimization terminated successfully. ',
                      1: 'Iteration limit reached. ',
                      2: 'Problem appears to be infeasible. ',
                      3: 'Problem appears to be unbounded. ',
                      4: 'Numerical difficulties encountered.'}

        demand_lst = np.zeros(len(self.item_array))
        for k, v in requirement_dct.items():
            demand_lst[self.item_dct_rv[k]] = v
        for k, v in deposited_dct.items():
            demand_lst[self.item_dct_rv[k]] -= v
        solution, dual_solution, excp_factor = self._get_plan_no_prioties(demand_lst, outcome, gold_demand, exp_demand)
        x, status = solution.x/excp_factor, solution.status
        y, self.slack = dual_solution.x, dual_solution.slack
        self.y = y
        n_looting, n_convertion = x[:len(self.cost_lst)], x[len(self.cost_lst):]

        cost = np.dot(x[:len(self.cost_lst)], self.cost_lst)

        if status != 0:
            raise ValueError(status_dct[status])

        self.stages = []
        self.fullstages = []
        self.effect = dict()
        for i, t in enumerate(n_looting):
#            if t >= 0:
#            self.effect[self.stage_array[i]] = sum([probsProb*self.item_values[self.item_array[[probsidx]]] for probsidx, probsProb in enumerate(self.probs_matrix[i])])/self.farm_cost[i]
#            if t >= 0.1:
            stage_name = self.stage_array[i]
            if stage_name[:2] in ['SK', 'AP', 'CE', 'LS', 'PR'] and self.display_main_only:
                continue
            target_items = np.where(self.probs_matrix[i]>0.01)[0]
            items = {self.item_array[idx]: float2str(self.probs_matrix[i, idx]*t)
            for idx in target_items if len(self.item_id_array[idx])<=5}
            stage = {
                "stage": self.stage_array[i],
                "count": float2str(t),
                "items": items
            }
            self.stages.append(stage)

        self.syntheses = []
        for i,t in enumerate(n_convertion):
            if t >= 0.1:
                target_item = self.item_array[np.argmax(self.convertion_matrix[i])]
                if target_item in ['经验', '龙门币']:
                    target_item_index = np.argmin(self.convertion_matrix[i])
                    materials = {self.item_array[target_item_index]:\
                        str(np.round(-self.convertion_matrix[i][target_item_index]*int(t+0.9),4))}
                else:
                    materials = {k: str(v*int(t+0.9)) for k,v in self.convertions_dct[target_item].items()}
                synthesis = {
                    "target": target_item,
                    "count": str(int(t+0.9)),
                    "materials": materials
                }
                self.syntheses.append(synthesis)
            elif t >= 0.05:
                target_item = self.item_array[np.argmax(self.convertion_matrix[i])]
                materials = { k: '%.1f'%(v*t) for k,v in self.convertions_dct[target_item].items() }
                synthesis = {
                    "target": target_item,
                    "count": '%.1f'%t,
                    "materials": materials
                }
                self.syntheses.append(synthesis)

        self.values = [{"level":'1', "items":[]},
                  {"level":'2', "items":[]},
                  {"level":'3', "items":[]},
                  {"level":'4', "items":[]},
                  {"level":'5', "items":[]},
                  {"level":'0', "items":[]}]

        self.item_value = dict()

        for i,item in enumerate(self.item_array):
            if y[i]>=0:
                if y[i]>0.1:
                    item_value = {
                        "name": item,
                        "value": '%.2f'%y[i]
                    }
                else:
                    item_value = {
                        "name": item,
                        "value": '%.5f'%(y[i])
                    }
                self.item_value[item] = y[i]
                self.values[int(self.item_id_array[i][-1])-1]['items'].append(item_value)
        self.item_value['寻访凭证'] = self.costLimit * 600 / 180
        self.item_value['合成玉'] = self.item_value['寻访凭证']/600
        self.item_value['芯片助剂'] = self.item_value['采购凭证'] * 90
        self.item_value['招聘许可'] = (20*self.公招出四星的概率+10)*self.item_value['糖组']/Price['糖组']+38/258*600/180*self.costLimit*self.公招出四星的概率 - self.item_value['龙门币']*774
        self.item_value['碳'] = (self.item_value['家具零件']*4-200*self.item_value['龙门币'])/(1-0.5*self.ConvertionDR)
        self.item_value['先锋皇家信物'] = self.item_value['采购凭证'] * 2000
        for group in self.values:
            group["items"] = sorted(group["items"], key=lambda k: float(k['value']), reverse=True)
#        self.values = sorted(self.values, key=lambda x: float(x['value']), reverse=True)
        for i, stage in enumerate(self.stage_array):
            self.effect[stage] = sum([probsProb*self.item_value[self.item_array[probsidx]] for probsidx, probsProb in enumerate(self.probs_matrix[i])])/self.farm_cost[i]
        self.res = {
            "cost": int(cost),
            "stages": self.stages,
            "syntheses": self.syntheses,
            "values": list(reversed(self.values))
        }

        self.output()
        return self.res, x, self.effect

    def merge_droprate(self):
        self.droprate = ddict(dict)
        for itemIndex, item in enumerate(self.item_array):
            for stageIndex, stage in enumerate(self.stage_array):
                dr = self.probs_matrix[stageIndex, itemIndex]
                if dr > 0.0001:
                    self.droprate[item][stage] = {
                                'droprate':         dr,
                                'expected_cost':    self.cost_lst[stageIndex]/dr,
                                'effect':           self.effect[stage]
                            }

    def stage_class(self, effect):
        if effect>0.99:
            return 'lowest_ap_stages'
        if effect>0.90:
            return 'balanced_stages'
        return 'drop_rate_first_stages'

    def output_best_stage(self, level='x'):
        '''
            筛选条件:  效率>0.99, 期望<1.2*最低期望
            效率<0.99, 掉率>当前最大掉率
            效率<0.99, 期望<当前最低期望
        '''
        # 活动时和主线比较
        MainStageMap = {
                         '异铁组': ['7-18'],
                         '轻锰矿': ['R8-10'],
                         '研磨石': ['7-17'],
                         '酮凝集组': ['JT8-3'],
                         'RMA70-12': ['R8-9'],
                         '装置': ['7-15'],
                         '扭转醇': ['R8-2'],
                         '糖组': ['4-2'],
                         '凝胶': ['JT8-2'],
                         '炽合金': ['R8-7'],
                         '固源岩': ['1-7'],
                         '聚酸酯组': ['7-4'],
                         '晶体元件': ['R8-11']
                        }
        self.merge_droprate()
        for item in self.item_array:
            if len(self.item_id_array[self.item_dct_rv[item]]) != 5 or item == '芯片助剂':
                continue
            itemLevel = self.item_id_array[self.item_dct_rv[item]][-1]
            if itemLevel != level:
                continue

            self.best_stage[item] = ddict(list)
            # 根据效率排序
            sorted_stages = sorted(self.droprate[item].items(), key=lambda x: x[1]['effect'], reverse=True)
            maxDropRate = max([x['droprate'] for x in self.droprate[item].values() if x['effect'] > 0.99]+[0.1])
            minExpect = min([x['expected_cost'] for x in self.droprate[item].values() if x['effect'] > 0.99]+[200 if self.costType == 'stone' else 2000])
            for stage, data in sorted_stages:
                if (data['droprate'] >= 1.25*maxDropRate) or\
                   (data['expected_cost'] <= 0.85*minExpect) or\
                   (data['effect'] > 0.98 and data['droprate'] > 0.8*maxDropRate and level=='3')or\
                   (data['effect'] > 0.98 and data['expected_cost'] <1.2*minExpect and level=='3')or\
                   (data['effect'] > 0.99 and data['droprate'] >= 0.9*maxDropRate)or\
                   (item in MainStageMap and stage in MainStageMap[item]):
                    maxDropRate = max(maxDropRate, data['droprate'])
                    minExpect = min(minExpect, data['expected_cost'])
                    toAppend = {
                            'code': stage,
                            'drop_rate': '%.3f'%data['droprate'],
                            'efficiency': '%.3f'%data['effect'],
                            'ap_per_item': '%.1f'%data['expected_cost'],
                            'extra_drop': list(self.output_main_drop(stage, item))
                            }
                    self.best_stage[item][self.stage_class(data['effect'])].append(toAppend)

    def output_droprate(self, stage):
        assert stage in self.stage_array
        for i, prob in enumerate(self.probs_matrix[self.stage_dct_rv[stage]]):
            if prob != 0:
                print(self.item_array[i], '\t%.3f' % (100*prob))

    def output_WeiJiHeYue(self):
        HeYue=CCStores[self.ccseason*2+2]
        HYO = CCStores[self.ccseason*2+3]

        self.HeYueDict = {
#                '龙门币': 85 * self.item_value['龙门币'] / 1,
#                '中级作战记录': self.item_value['中级作战记录'] / 12,
#                '技巧概要·卷2(刷CA3)': 20/(3 + 1.18/3) / 15 *(1-self.gold_unit*1*12),
#                '技巧概要·卷2(不刷CA3)': self.item_value['技巧概要·卷2'] / 15,
#                '技巧概要·卷2(不刷CA3)': 30/(4 + 3*1.18/3 + 3*1.18*1.18/3/3)*2/3*1.18 / 15*(1-self.gold_unit*1*12),
#                '芯片': (18-0.165*0.5*18/3)/(0.5 + 0.5*2/3)/60*(1-self.gold_unit*1*12)
                 }
        self.HYODict = {
                '柏喙': self.item_value['采购凭证'] * 600 / 300 
#                '龙门币': 2000 * self.gold_unit / 15,
#                '中级作战记录': self.exp_unit*5*2 / 15,
#                '零件': 1/1.8,
#                '皮肤': 21*self.costLimit/3000
                }
        for item, value in HeYue.items():
            if item == '近卫，狙击，辅助或重装芯片':
                self.HeYueDict[item] = self.item_value['近卫芯片'] / value
            elif item == '术师，特种，医疗或先锋芯片':
                self.HeYueDict[item] = self.item_value['特种芯片']/ value
            else:
                self.HeYueDict[item] = self.item_value[item] / value
        self.item_value['高级作战记录'] = 2*self.item_value['中级作战记录']

        for item, value in HYO.items():
            self.HYODict[item] = self.item_value[item] / value
        if not self.print_output:
            return
        print('\n机密圣所(合约商店):')
        for k, v in sorted(self.HeYueDict.items(), key=lambda x:x[1], reverse=True):
            print('%s:\t%.3f'%(k, v))
        print('常规池')
        for k, v in sorted(self.HYODict.items(), key=lambda x:x[1], reverse=True):
            print('%s:\t%.3f'%(k, v))

    def output(self):
        Print_functions = [
            self.output_cost,
            self.output_stages,
            self.output_items,
            self.output_values,
            self.output_green,
            self.output_yellow,
            self.output_effect,
            self.output_best_stage,
            self.output_credit,
            self.output_WeiJiHeYue,
            self.output_orange,
            self.output_purple
        ]
        for i, function in enumerate(Print_functions):
            if self.printSetting[i]:
                Print_functions[i]()
        return

    def output_cost(self):
        print('消耗理智 %d = %d 天, 相当于碎石 %d 颗, %d 元'%\
                  (self.res['cost'], int(self.res['cost']/self.everyday_cost), np.round(self.res['cost']/self.costLimit),
                   np.round(self.res['cost']/self.costLimit*648/185)))
        if self.costType == 'time':
            print('消耗时间 %d 秒 = %.2f天'%\
                      (self.res['cost'], self.res['cost']/86400))

    def output_stages(self):
        print('Loot at following stages:')
        for stage in self.stages:
            if float(stage['count']) > 1:
#                print(stage['items'])
                display_lst = [k + '(%s) '%v for k, v in sorted(stage['items'].items(), key=lambda x: (float(x[1])*self.item_value[x[0]]), reverse=True)][:5]
#                if stage['stage'] not in ['LS-5', 'CE-5']:
#                    display_lst = display_lst[1:] + [display_lst[0]]
                print(stage['stage'] + '(%s 次) ===> '%stage['count']
                                     + ', '.join(display_lst))

    def output_main_drop(self, stage_name, target_item, gate=0.1, output=False):
        stageID = self.stage_dct_rv[stage_name]
        farm_cost = self.farm_cost[stageID]
        itemPercentage = [(self.item_value[self.item_array[k]]*v/farm_cost, self.item_array[k])
                            for k,v in enumerate(self.probs_matrix[stageID])]
        display_lst = [x for x in sorted(itemPercentage, key=lambda x:x[0], reverse=True) if x[0] > gate]
        if output:
            print(display_lst)
        for value, item in display_lst:
#            sys.stdout.write('%.3f\t%s\n' % (value, item))
            if item != target_item:
                if item == '初级作战记录': item = '基础作战记录'
                if item == '龙门币': continue
                yield {'name': item, 'id': self.item_name_to_id[item]}

    def output_items(self):
        print('\nSynthesize following items:')
        for synthesis in self.syntheses:
            display_lst = [k + '(%s) '%synthesis['materials'][k] for k in synthesis['materials']]
            print(synthesis['target'] + '(%s) <=== '%synthesis['count']
            + ', '.join(display_lst))

    def output_values(self):
        print('[collapse=材料价值]')
        for i, group in reversed(list(enumerate(self.values))):
            display_lst = ['%s:%.6s'%(item['name'], self.item_value[item['name']]) for item in group['items']]
            if i == 5:
#                display_lst.append('罗德岛物资补给:%.2f'%((self.effect['罗德岛物资补给'])*99-99*12*self.item_value['龙门币']))
                print('特殊材料:')
                print(', '.join(display_lst))
                continue
            print('%d级材料: '%(i+1))
            print(', '.join(display_lst))
#        for x in self.values:
#            print('%s:\t %s' % (x['name'], x['value']))
#        print('特殊材料:\n罗德岛物资补给:%.2f'%(self.effect['罗德岛物资补给']*99))
        sys.stdout.write('[/collapse]')

    def output_green(self):
        self.greenTickets = {'招聘许可': self.item_value['招聘许可'] / Price['招聘许可'],
                             '寻访凭证': self.item_value['寻访凭证'] / Price['寻访凭证']}

        for item in self.values[2]['items']:
            try:
                self.greenTickets[item['name']] = self.item_value[item['name']] / Price[item['name']]
            except:
                pass
        for k, item in enumerate(sorted(self.greenTickets.items(), key=lambda x:x[1], reverse=True)):
            if k < 0.25*len(self.greenTickets):
                self.Notes[item[0]] = 'red'
            elif k < 0.5*len(self.greenTickets):
                self.Notes[item[0]] = 'yellow'
            elif k < 0.75*len(self.greenTickets):
                self.Notes[item[0]] = 'green'
            else:
                self.Notes[item[0]] = ''
        if not self.print_output:
            return
        print('[collapse=绿票商店]')
        for k, v in sorted(self.greenTickets.items(), key=lambda x:x[1], reverse=True):
            print('%s:\t%.3f'%(k, v))
        sys.stdout.write('[/collapse]')

    def output_orange(self):
        self.orangeTickets = {}
        for item, value in Orange.items():
            self.orangeTickets[item] = self.item_value[item] / value
        self.orangeNotes = {}
        for k, item in enumerate(sorted(self.orangeTickets.items(), key=lambda x:x[1], reverse=True)):
            if k < 0.25*len(self.orangeTickets):
                self.orangeNotes[item[0]] = 'red'
            elif k < 0.5*len(self.orangeTickets):
                self.orangeNotes[item[0]] = 'yellow'
            elif k < 0.75*len(self.orangeTickets):
                self.orangeNotes[item[0]] = 'green'
            else:
                self.orangeNotes[item[0]] = ''
        print('[collapse=橙票商店]')
        for k, v in sorted(self.orangeTickets.items(), key=lambda x:x[1], reverse=True):
            print('%s:\t%.3f'%(k, v))
        sys.stdout.write('[/collapse]')

    def output_purple(self):
        self.purpleTickets = {}
        for item, value in Purple.items():
            self.purpleTickets[item] = self.item_value[item] / value
        self.purpleNotes = {}
        for k, item in enumerate(sorted(self.purpleTickets.items(), key=lambda x: x[1], reverse=True)):
            if k < 0.25 * len(self.purpleTickets):
                self.purpleNotes[item[0]] = 'red'
            elif k < 0.5 * len(self.orangeTickets):
                self.purpleNotes[item[0]] = 'yellow'
            elif k < 0.75 * len(self.orangeTickets):
                self.purpleNotes[item[0]] = 'green'
            else:
                self.purpleNotes[item[0]] = ''
        print('[collapse=紫票商店]')
        for k, v in sorted(self.purpleTickets.items(), key=lambda x: x[1], reverse=True):
            print('%s:\t%.3f' % (k, v))
        sys.stdout.write('[/collapse]')


    def output_yellow(self):
        self.yellowTickets = {'芯片助剂': self.item_value['芯片助剂'] / Price['芯片助剂']}
        for item in self.values[3]['items']:
            try:
                self.yellowTickets[item['name']] = self.item_value[item['name']] / Price[item['name']]
            except:
                pass
        for k, item in enumerate(sorted(self.yellowTickets.items(), key=lambda x:x[1], reverse=True)):
            if k < 0.25*len(self.yellowTickets):
                self.Notes[item[0]] = 'red'
            elif k < 0.5*len(self.yellowTickets):
                self.Notes[item[0]] = 'yellow'
            elif k < 0.75*len(self.yellowTickets):
                self.Notes[item[0]] = 'green'
            else:
                self.Notes[item[0]] = ''
        if not self.print_output:
            return
        print('[collapse=黄票商店]')
        for k, v in sorted(self.yellowTickets.items(), key=lambda x:x[1], reverse=True):
            print('%s:\t%.3f'%(k, v))
        sys.stdout.write('[/collapse]')

    def output_credit(self):
        self.creditEffect = dict()
        for item, value in Credit.items():
            self.creditEffect[item] = self.item_value[item]/value

        for k, item in enumerate(sorted(self.creditEffect.items(), key=lambda x:x[1], reverse=True)):
            if k < 0.25*len(self.creditEffect):
                self.Notes[item[0]] = 'red'
            elif k < 0.5*len(self.creditEffect):
                self.Notes[item[0]] = 'yellow'
            elif k < 0.75*len(self.creditEffect):
                self.Notes[item[0]] = 'green'
            else:
                self.Notes[item[0]] = ''
        if not self.print_output:
            return
        print('[collapse=信用商店]')
        for item, value in sorted(self.creditEffect.items(), key=lambda x:x[1], reverse=True):
            print('%-20s:\t\t%.3f' % (item, value*100))
#            sys.stdout.write('%s>'%item)
        sys.stdout.write('[/collapse]')

    def output_effect(self, filter=None):
        print('[collapse=关卡效率]')
        for k, v in sorted(self.effect.items(), key=lambda x:x[1], reverse=True):
#            if v < 0.9:
#                break
            if filter and filter not in k:
                continue
            if k[:2] in ['SK', 'AP', 'CE', 'LS', 'PR'] and self.display_main_only:
                continue
            if 'AF' in k[:2]:
                print('[b]%9s:\t%.2f\t(%d 样本)[/b]'%(k, v*100, self.stage_times[k]))
            else:
                print('%9s:\t%.2f\t(%d 样本)'%(k, v*100, self.stage_times[k]))
        sys.stdout.write('[/collapse]')

    def update_droprate_processing(self, stage, item, droprate, mode='add'):
        if stage not in self.stage_array:
            print('关卡%s被禁用, 材料%s添加失败.'%(stage, item))
            return
        if item not in self.item_array:
            print('材料%s被禁用, 关卡%s添加失败.'%(item, stage))
            return
        stageid = self.stage_dct_rv[stage]
        itemid = self.item_dct_rv[item]
        if mode == 'add':
            self.probs_matrix[stageid][itemid] += droprate
        elif mode == 'update':
            self.probs_matrix[stageid][itemid] = droprate
        else:
            print('关卡%s, 材料%s, 模式错误添加失败'%(stage, item))

    def update_stage_processing(self, stage_name: str, cost: int):
        if stage_name not in self.stage_array:
            self.stage_array.append(stage_name)
            self.stage_dct_rv.update({stage_name: len(self.stage_array)-1})
            self.cost_lst = np.append(self.cost_lst, cost)
        else:
            self.cost_lst[self.stage_dct_rv[stage_name]] = cost

    def update_droprate(self):
        self.update_droprate_processing('S4-6', '龙门币', 3228)
        self.update_droprate_processing('S5-2', '龙门币', 2484)
        self.update_droprate_processing('S6-4', '龙门币', 2700, 'update')
        self.update_droprate_processing('SK-1', '家具零件', 1, 'update')
        self.update_droprate_processing('SK-2', '家具零件', 3, 'update')
        self.update_droprate_processing('SK-3', '家具零件', 5, 'update')
        self.update_droprate_processing('SK-4', '家具零件', 7, 'update')
        self.update_droprate_processing('SK-5', '家具零件', 10, 'update')
        self.update_droprate_processing('CE-1', '龙门币', 1700, 'update')
        self.update_droprate_processing('CE-2', '龙门币', 2800, 'update')
        self.update_droprate_processing('CE-3', '龙门币', 4100, 'update')
        self.update_droprate_processing('CE-4', '龙门币', 5700, 'update')
        self.update_droprate_processing('CE-5', '龙门币', 7500, 'update')
        '''
        self.update_droprate_processing('LS-1', '经验', 1600, 'update')
        self.update_droprate_processing('LS-2', '经验', 2800, 'update')
        self.update_droprate_processing('LS-3', '经验', 3900, 'update')
        self.update_droprate_processing('LS-4', '经验', 5900, 'update')
        self.update_droprate_processing('LS-5', '经验', 7400, 'update')
        '''
        self.update_droprate_processing('AP-5', '采购凭证', 21, 'update')

        self.update_droprate_processing('PR-A-1', '重装芯片', 1/2, 'update')
        self.update_droprate_processing('PR-A-1', '医疗芯片', 1/2, 'update')
        self.update_droprate_processing('PR-B-1', '狙击芯片', 1/2, 'update')
        self.update_droprate_processing('PR-B-1', '术师芯片', 1/2, 'update')
        self.update_droprate_processing('PR-C-1', '先锋芯片', 1/2, 'update')
        self.update_droprate_processing('PR-C-1', '辅助芯片', 1/2, 'update')
        self.update_droprate_processing('PR-D-1', '近卫芯片', 1/2, 'update')
        self.update_droprate_processing('PR-D-1', '特种芯片', 1/2, 'update')
        self.update_droprate_processing('PR-A-2', '重装芯片组', 1/2, 'update')
        self.update_droprate_processing('PR-A-2', '医疗芯片组', 1/2, 'update')
        self.update_droprate_processing('PR-B-2', '狙击芯片组', 1/2, 'update')
        self.update_droprate_processing('PR-B-2', '术师芯片组', 1/2, 'update')
        self.update_droprate_processing('PR-C-2', '先锋芯片组', 1/2, 'update')
        self.update_droprate_processing('PR-C-2', '辅助芯片组', 1/2, 'update')
        self.update_droprate_processing('PR-D-2', '近卫芯片组', 1/2, 'update')
        self.update_droprate_processing('PR-D-2', '特种芯片组', 1/2, 'update')

        for i, stage in enumerate(self.stage_array):
            self.update_droprate_processing(stage, '龙门币', self.base_gold/self.everyday_cost*self.cost_lst[i], 'add')
            self.update_droprate_processing(stage, '赤金', -self.base_gold/500/self.everyday_cost*self.cost_lst[i], 'add')
            self.update_droprate_processing(stage, '经验', self.base_exp/self.everyday_cost*self.cost_lst[i], 'add')
            self.update_droprate_processing(stage, '赤金', self.base_MTL_GOLD3/500/self.everyday_cost*self.cost_lst[i], 'add')

    def update_convertion_processing(self, target_item: tuple, cost: int, source_item: dict, extraOutcome: dict):
        '''
            target_item: (item, itemCount)
            cost: number of 龙门币
            source_item: {item: itemCount}
            extraOutcome: {outcome: {item: weight}, rate, totalWeight}
        '''
        toAppend = dict()
        Outcome, rate, totalWeight = extraOutcome
        toAppend['costs'] = [{'count':x[1]/target_item[1], 'id':self.item_dct_rv[x[0]], 'name':x[0]} for x in source_item.items()]
        toAppend['extraOutcome'] = [{'count': rate, 'id': self.item_dct_rv[x[0]], 'name': x[0], 'weight': x[1]/target_item[1]} for x in Outcome.items()]
        toAppend['goldCost'] = cost/target_item[1]
        toAppend['id'] = self.item_dct_rv[target_item[0]]
        toAppend['name'] = target_item[0]
        toAppend['totalWeight'] = totalWeight
        self.convertion_rules.append(toAppend)

    def update_convertion(self):
        # 考虑 岁过华灯 的影响
        if self.SuiGuoHuaDeng:
            weight = {self.item_array[item]: dr for item, dr in enumerate(self.probs_matrix[self.stage_dct_rv['岁过华灯']]) if self.item_array[item] != '龙门币'}
            self.update_convertion_processing(('龙门币', 1), 1, {'岁过华灯': 1}, (weight, 1/0.18, 1))
        self.update_convertion_processing(('技巧概要·卷3', 1), 0, {'技巧概要·卷2': 3}, ({'技巧概要·卷3':1}, 1, 1))
        self.update_convertion_processing(('技巧概要·卷2', 1), 0, {'技巧概要·卷1': 3}, ({'技巧概要·卷2':1}, 1, 1))
        self.update_convertion_processing(('经验', 200), 0, {'基础作战记录': 1}, ({}, 0, 1))
        self.update_convertion_processing(('经验', 400), 0, {'初级作战记录': 1}, ({}, 0, 1))
        self.update_convertion_processing(('经验', 1000), 0, {'中级作战记录': 1}, ({}, 0, 1))
        self.update_convertion_processing(('经验', 2000), 0, {'高级作战记录': 1}, ({}, 0, 1))
        self.update_convertion_processing(('经验', 400), 0, {'赤金': 1}, ({}, 0, 1))
        self.update_convertion_processing(('家具零件', 4), 200, {'碳': 1}, ({'碳': 1}, 0.5, 1))
        self.update_convertion_processing(('家具零件', 8), 200, {'碳素': 1}, ({'碳素': 1}, 0.5, 1))
        self.update_convertion_processing(('家具零件', 12), 200, {'碳素组': 1}, ({'碳素组': 1}, 0.5, 1))
        self.update_convertion_processing(('重装芯片', 2), 0, {'医疗芯片': 3}, ({'重装芯片': 1, '医疗芯片':1,
                '狙击芯片': 1, '术师芯片': 1, '先锋芯片': 1, '辅助芯片': 1, '近卫芯片': 1, '特种芯片': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('医疗芯片', 2), 0, {'重装芯片': 3}, ({'重装芯片': 1, '医疗芯片':1,
                '狙击芯片': 1, '术师芯片': 1, '先锋芯片': 1, '辅助芯片': 1, '近卫芯片': 1, '特种芯片': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('狙击芯片', 2), 0, {'术师芯片': 3}, ({'重装芯片': 1, '医疗芯片':1,
                '狙击芯片': 1, '术师芯片': 1, '先锋芯片': 1, '辅助芯片': 1, '近卫芯片': 1, '特种芯片': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('术师芯片', 2), 0, {'狙击芯片': 3}, ({'重装芯片': 1, '医疗芯片':1,
                '狙击芯片': 1, '术师芯片': 1, '先锋芯片': 1, '辅助芯片': 1, '近卫芯片': 1, '特种芯片': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('先锋芯片', 2), 0, {'辅助芯片': 3}, ({'重装芯片': 1, '医疗芯片':1,
                '狙击芯片': 1, '术师芯片': 1, '先锋芯片': 1, '辅助芯片': 1, '近卫芯片': 1, '特种芯片': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('辅助芯片', 2), 0, {'先锋芯片': 3}, ({'重装芯片': 1, '医疗芯片':1,
                '狙击芯片': 1, '术师芯片': 1, '先锋芯片': 1, '辅助芯片': 1, '近卫芯片': 1, '特种芯片': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('特种芯片', 2), 0, {'近卫芯片': 3}, ({'重装芯片': 1, '医疗芯片':1,
                '狙击芯片': 1, '术师芯片': 1, '先锋芯片': 1, '辅助芯片': 1, '近卫芯片': 1, '特种芯片': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('近卫芯片', 2), 0, {'特种芯片': 3}, ({'重装芯片': 1, '医疗芯片':1,
                '狙击芯片': 1, '术师芯片': 1, '先锋芯片': 1, '辅助芯片': 1, '近卫芯片': 1, '特种芯片': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('重装芯片组', 2), 0, {'医疗芯片组': 3}, ({'重装芯片组': 1, '医疗芯片组':1,
                '狙击芯片组': 1, '术师芯片组': 1, '先锋芯片组': 1, '辅助芯片组': 1, '近卫芯片组': 1, '特种芯片组': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('医疗芯片组', 2), 0, {'重装芯片组': 3}, ({'重装芯片组': 1, '医疗芯片组':1,
                '狙击芯片组': 1, '术师芯片组': 1, '先锋芯片组': 1, '辅助芯片组': 1, '近卫芯片组': 1, '特种芯片组': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('狙击芯片组', 2), 0, {'术师芯片组': 3}, ({'重装芯片组': 1, '医疗芯片组':1,
                '狙击芯片组': 1, '术师芯片组': 1, '先锋芯片组': 1, '辅助芯片组': 1, '近卫芯片组': 1, '特种芯片组': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('术师芯片组', 2), 0, {'狙击芯片组': 3}, ({'重装芯片组': 1, '医疗芯片组':1,
                '狙击芯片组': 1, '术师芯片组': 1, '先锋芯片组': 1, '辅助芯片组': 1, '近卫芯片组': 1, '特种芯片组': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('先锋芯片组', 2), 0, {'辅助芯片组': 3}, ({'重装芯片组': 1, '医疗芯片组':1,
                '狙击芯片组': 1, '术师芯片组': 1, '先锋芯片组': 1, '辅助芯片组': 1, '近卫芯片组': 1, '特种芯片组': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('辅助芯片组', 2), 0, {'先锋芯片组': 3}, ({'重装芯片组': 1, '医疗芯片组':1,
                '狙击芯片组': 1, '术师芯片组': 1, '先锋芯片组': 1, '辅助芯片组': 1, '近卫芯片组': 1, '特种芯片组': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('特种芯片组', 2), 0, {'近卫芯片组': 3}, ({'重装芯片组': 1, '医疗芯片组':1,
                '狙击芯片组': 1, '术师芯片组': 1, '先锋芯片组': 1, '辅助芯片组': 1, '近卫芯片组': 1, '特种芯片组': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('近卫芯片组', 2), 0, {'特种芯片组': 3}, ({'重装芯片组': 1, '医疗芯片组':1,
                '狙击芯片组': 1, '术师芯片组': 1, '先锋芯片组': 1, '辅助芯片组': 1, '近卫芯片组': 1, '特种芯片组': 1}, 0.165/0.18, 8))
        self.update_convertion_processing(('近卫双芯片', 1), 0, {'近卫芯片组': 2, '经验': 1000/3, '采购凭证': 90}, ({}, 0, 1))
        self.update_convertion_processing(('重装双芯片', 1), 0, {'重装芯片组': 2, '经验': 1000/3, '采购凭证': 90}, ({}, 0, 1))
        self.update_convertion_processing(('医疗双芯片', 1), 0, {'医疗芯片组': 2, '经验': 1000/3, '采购凭证': 90}, ({}, 0, 1))
        self.update_convertion_processing(('特种双芯片', 1), 0, {'特种芯片组': 2, '经验': 1000/3, '采购凭证': 90}, ({}, 0, 1))
        self.update_convertion_processing(('辅助双芯片', 1), 0, {'辅助芯片组': 2, '经验': 1000/3, '采购凭证': 90}, ({}, 0, 1))
        self.update_convertion_processing(('术师双芯片', 1), 0, {'术师芯片组': 2, '经验': 1000/3, '采购凭证': 90}, ({}, 0, 1))
        self.update_convertion_processing(('狙击双芯片', 1), 0, {'狙击芯片组': 2, '经验': 1000/3, '采购凭证': 90}, ({}, 0, 1))
        self.update_convertion_processing(('先锋双芯片', 1), 0, {'先锋芯片组': 2, '经验': 1000/3, '采购凭证': 90}, ({}, 0, 1))
        if self.ExpFromBase:
            self.update_convertion_processing(('经验', 1000), 0, {'龙门币': 625}, ({}, 0, 1))


    def update_stage(self):
        self.update_stage_processing('PR-A-1', 18)
        self.update_stage_processing('PR-A-2', 36)
        self.update_stage_processing('PR-B-1', 18)
        self.update_stage_processing('PR-B-2', 36)
        self.update_stage_processing('PR-C-1', 18)
        self.update_stage_processing('PR-C-2', 36)
        self.update_stage_processing('PR-D-1', 18)
        self.update_stage_processing('PR-D-2', 36)
        self.update_stage_processing('CE-1', 10)
        self.update_stage_processing('CE-2', 15)
        self.update_stage_processing('CE-3', 20)
        self.update_stage_processing('CE-4', 25)
        self.update_stage_processing('CE-5', 30)
        self.update_stage_processing('LS-1', 10)
        self.update_stage_processing('LS-2', 15)
        self.update_stage_processing('LS-3', 20)
        self.update_stage_processing('LS-4', 25)
        self.update_stage_processing('LS-5', 30)
        self.update_stage_processing('SK-1', 10)
        self.update_stage_processing('SK-2', 15)
        self.update_stage_processing('SK-3', 20)
        self.update_stage_processing('SK-4', 25)
        self.update_stage_processing('SK-5', 30)
        self.update_stage_processing('AP-5', 30)



def Cartesian_sum(arr1, arr2):
    arr_r = []
    for arr in arr1:
        arr_r.append(arr+arr2)
    arr_r = np.vstack(arr_r)
    return arr_r

def float2str(x, offset=0.5):

    if x < 1.0:
        out = '%.1f'%x
    else:
        out = '%d'%(int(x+offset))
    return out

def request_data(url_stats, url_rules, url_items, url_stages,
                 save_path_stats, save_path_rules, save_path_items, save_path_stages):
    """
    To request probability and convertion rules from web resources and store at local.
    Args:
        url_stats: string. url to the dropping rate stats data.
        url_rules: string. url to the composing rules data.
        save_path_stats: string. local path for storing the stats data.
        save_path_rules: string. local path for storing the composing rules data.
    Returns:
        material_probs: dictionary. Content of the stats json file.
        convertion_rules: dictionary. Content of the rules json file.
    """
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
    try:
        os.mkdir(os.path.dirname(save_path_stats))
    except:
        pass
    try:
        os.mkdir(os.path.dirname(save_path_rules))
    except:
        pass
    try:
        os.mkdir(os.path.dirname(save_path_items))
    except:
        pass
    try:
        os.mkdir(os.path.dirname(save_path_stages))
    except:
        pass
    page_stats = urllib.request.Request(url_stats, headers=headers)
    with urllib.request.urlopen(page_stats) as url:
        material_probs = json.loads(url.read().decode())
        with open(save_path_stats, 'w') as outfile:
            json.dump(material_probs, outfile)

    page_rules = urllib.request.Request(url_rules, headers=headers)
    with urllib.request.urlopen(page_rules) as url:
        convertion_rules = json.loads(url.read().decode())
        with open(save_path_rules, 'w') as outfile:
            json.dump(convertion_rules, outfile)

    page_stats = urllib.request.Request(url_items, headers=headers)
    with urllib.request.urlopen(page_stats) as url:
        item_list = json.loads(url.read().decode())
        item_list = {x['itemId']: x['name'] for x in item_list}
        with open(save_path_items, 'w') as outfile:
            json.dump(item_list, outfile)

    page_stats = urllib.request.Request(url_stages, headers=headers)
    with urllib.request.urlopen(page_stats) as url:
        stage_list = json.loads(url.read().decode())
        stage_list = {x['stageId']: {'code': x['code'], 'cost': x['apCost']} for x in stage_list}
        with open(save_path_stages, 'w') as outfile:
            json.dump(stage_list, outfile)

    return material_probs, convertion_rules, item_list, stage_list

def load_data(path_stats, path_rules, path_items, path_stages):
    """
    To load stats and rules data from local directories.
    Args:
        path_stats: string. local path to the stats data.
        path_rules: string. local path to the composing rules data.
    Returns:
        material_probs: dictionary. Content of the stats json file.
        convertion_rules: dictionary. Content of the rules json file.
    """
    with open(path_stats) as json_file:
        material_probs  = json.load(json_file)
    with open(path_rules) as json_file:
        convertion_rules  = json.load(json_file)

    with open(path_items) as json_file:
        items  = json.load(json_file)
    with open(path_stages) as json_file:
        stages  = json.load(json_file)

    return material_probs, convertion_rules, items, stages