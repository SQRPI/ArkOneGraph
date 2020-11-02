# -*- coding: utf-8 -*-

from MaterialPlanning import MaterialPlanning

#from MaterialPlanningRaw import MaterialPlanning as MPR
#from utils import required_dctCN, owned_dct
required_dctCN = {'D32钢': 382, '双极纳米片': 454, 'D32钢': 382, '聚合剂': 378, '白马醇': 476, '扭转醇': 339, '三水锰矿': 399, '轻锰矿': 229, '五水研磨石': 458, '研磨石': 237, 'RMA70-24': 430, 'RMA70-12': 218, '提纯源岩': 446, '固源岩组': 329, '固源岩': 259, '源岩': 217, '改量装置': 306, '全新装置': 198, '装置': 116, '破损装置': 96, '聚酸酯块': 316, '聚酸酯组': 140, '聚酸酯': 201, '酯原料': 149, '糖聚块': 303, '糖组': 135, '糖': 194, '代糖': 153, '异铁块': 392, '异铁组': 201, '异铁': 176, '异铁碎片': 120, '酮阵列': 426, '酮凝集组': 339, '酮凝集': 166, '双酮': 123, '聚合凝胶': 384, '凝胶': 261, '炽合金块': 366, '炽合金': 248, '近卫双芯片': 50, '重装双芯片': 20, '狙击双芯片': 35, '医疗双芯片': 25, '辅助双芯片': 15, '特种双芯片': 25, '术师双芯片': 20, '先锋双芯片': 20, '近卫芯片组': 67, '重装芯片组': 37, '狙击芯片组': 46, '医疗芯片组': 26, '辅助芯片组': 36, '特种芯片组': 30, '术师芯片组': 43, '先锋芯片组': 26, '近卫芯片': 117, '重装芯片': 60, '狙击芯片': 81, '医疗芯片': 49, '辅助芯片': 56, '特种芯片': 54, '术师芯片': 68, '先锋芯片': 46, '经验': 102334800, '龙门币': 114019816, '家具零件': 10000, '采购凭证': 1000, '技巧概要·卷1': 1028, '技巧概要·卷2': 2295, '技巧概要·卷3': 7562}
N = 100
required_dctCN.update({
  '晶体电路':   N,
  '晶体元件':   N,
  '晶体电子单元': N
})
owned_dct = {}
'''
        Print_functions = [
            self.output_cost,           #理智消耗
            self.output_stages,         #关卡次数
            self.output_items,          #合成次数
            self.output_values,         #物品价值
            self.output_green,          #绿票商店
            self.output_yellow,         #黄票商店
            self.output_effect,         #关卡效率
            self.output_best_stage,     #关卡推荐
            self.output_credit,         #信用商店
            self.output_WeiJiHeYue      #危机合约(喧闹法则活动商店)
            ]
'''

if True:
    prst = '010100000000' if __name__ == '__main__' else '000011001011'
#    prst = '0000000000' if __name__ == '__main__' else '0000110010'
    print_output = True if __name__ == '__main__' else False
    update = False if __name__ == '__main__' else True
    SuiGuoHuaDeng = False if __name__ == '__main__' else False
    ExpFromBase = False if __name__ == '__main__' else False

    mp = MaterialPlanning(filter_stages=['荒芜行动物资补给', '罗德岛物资补给', '岁过华灯'],
                          filter_freq=100,
                          update=update,
                          banned_stages={},
#                          expValue=30,                 #1224更新后此参数无效, 使用经验需求来调节经验价值
                          printSetting=prst,    #参照上面Print_functions的顺序设置, 1输出, 0不输出
                          ConvertionDR=0.18,            #副产物掉落率
                          costLimit=135,                 #理智上限
                          #costType='time',
                          base_exp=0,
                          base_MTL_GOLD3=0,
                          base_gold=0,
                          stone_per_day=0,
                          display_main_only=True,
                          SuiGuoHuaDeng=SuiGuoHuaDeng,
                          ExpFromBase = ExpFromBase
                          )

#    mpr = MPR()
    res, mat1, mat2 = mp.get_plan(required_dctCN, owned_dct, print_output=print_output, outcome=True,
                                  gold_demand=True, exp_demand=True)
    print('发布前记得确认材料需求是否正确!')
#    print(mp.effect['1-7'])
#    mpr.get_plan(required_dct, owned_dct, print_output=True, outcome=True,
#                                  gold_demand=True, exp_demand=True)
