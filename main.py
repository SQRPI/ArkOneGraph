from MaterialPlanning import MaterialPlanning
#from MaterialPlanningRaw import MaterialPlanning as MPR
from utils import required_dct, owned_dct

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
    prst = '11111110111' if __name__ == '__main__' else '00001100101'
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
    res, mat1, mat2 = mp.get_plan(required_dct, owned_dct, print_output=print_output, outcome=True,
                                  gold_demand=True, exp_demand=True)
    print('发布前记得确认材料需求是否正确!')
#    print(mp.effect['1-7'])
#    mpr.get_plan(required_dct, owned_dct, print_output=True, outcome=True,
#                                  gold_demand=True, exp_demand=True)
