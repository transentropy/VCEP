# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 16:48:19 2019
-
@author: user
"""
import requests
import json
import re

divide = {"op":"",
          "ed":"",
          "ch":[],
          "hh":['/'],
          'hc':[':', '：'],
          'cc':['/', '、']
          }

word = '-\u4e00-\u9fa5 _.@a-zA-Z0-9'

jobList = ['策划', '作曲', '编曲', '作词', '调教', '混音', '母带', '人设', '曲绘',
       '封面', 'PV', '题字', 'LOGO', '美工', '列表外其他','协力', '宣传', '特别感谢', '演唱', '出品']

jobDictZH = {'作':{'曲':1, '词':3, 'default':1},
           '曲':{'作':1, '绘':8, 'default':1},
           '编':{'曲':2, 'default':2},
           '词':{'作':3, 'default':3},
           '调':{'音':4, '教':4, '校':4, 'default':4},
           '混':{'音':5, 'default':5},
           '绘':{'画':8, '图':8, '制':8, 'default':8},
           '画':{'师':8, 'default':8},
           '演':{'唱':-2, 'default':'+'},
           '视':{'频':10, 'default':10},
           '影':{'default': 10},
           '映':{'像':10, '画':10, 'default':10},
           '唱':{'default': -2},
           '歌':{'手': -2, 'default': -2},
           '协':{'力':-5, '助':-5, 'default':-5},
           '策':{'划':0, 'default':0},
           '呗':{'default':-2},
           '母':{'带':6, 'default':'+'},
           '出':{'品':-1, 'default':'+'},
           '封':{'面':9, 'default':9},
           '宣':{'传':-4, 'default':-4},
           '题':{'字':11, 'default':'+'},
           '美':{'工':13, 'default':'+'},
           'default':''
           }

jobDictEN = {'pv':10,
             '^mus':1,
             'pro':2,
             '^comp':2,
             '^lyr':3,
             '^mix':5,
             '^thank':-3,
             '^spe':-3,
             '^v':4,
             '^tu':4,
             '^illu':8,
             '^mov':10,
             'logo':12,
             }

class Intro:
    def __init__(self, text, divide):
        self.text = text
        self.divide = divide
        self.forbid = [["^http", "简介补充", "曲目类型", '本家$', '^原'], ["^http", "^av", "^www"]]
        self.pattern = re.compile(self.partternMaker())
        self.stfLi = self.extract()
        self.autoCheck()
        self.autoParse()
        
    def insert(self, index, obj):
        self.stfLi.insert(index, obj)
        
    def appand(self, obj):
        self.stfLi.append(obj)
        
    def remove(self, index):
        return self.stfLi.pop(index)
        
    def exchange(self, index1, index2):
        tmp = self.stfLi[index1]
        self.stfLi[index1] = self.stfLi[index2]
        self.stfLi[index2] = tmp
        
    def move(self, oriIndex, newIndex):
        tmp = self.remove(oriIndex)
        self.iinsert(newIndex, tmp)
        
    def update(self, index, obj):
        self.stfLi[index] = obj
        
    def extract(self):
        pat = re.compile(self.divide['op'] + "(.|\s)+" +self.divide['ed'])
        brickList = self.pattern.findall(re.search(pat, self.text).group())
        staffList = []
        for row in brickList:
            staffList.append(re.split("[" + "".join(self.divide['hc']) + "]", row))
        index = 0
        while index < len(staffList):
            staffList[index] = [re.split("[" + "".join(self.divide['hh']) + "]", staffList[index][0]),
                                re.split("[" + "".join(self.divide['cc']) + "]", staffList[index][1])]
            index = index + 1
        return staffList
    
    def autoCheck(self):
        index = 0
        while index < len(self.stfLi):
            forbid = False
            for job in self.stfLi[index][0]:
                for pat in self.forbid[0]:
                    if re.match(pat, job):
                        forbid = True; break

            else:
                for name in self.stfLi[index][1]:
                    for pat in self.forbid[1]:
                        if re.match(pat, name):
                            forbid = True; break
            
            if forbid:
                self.remove(index)
                continue
            index = index + 1
        return
    
    def getIndex(self, elem):
        return elem[2]
    
    def autoParse(self):
        index = 0
        while index < len(self.stfLi):
            tmpList = []
            sort = len(jobList) - 5
            for jobs in self.stfLi[index][0]:
                tmp = self.staffParse(jobs)
                if tmp[0] < 0:
                    tmp[0] = tmp[0] + len(jobList)
                if sort > tmp[0]:
                    sort = tmp[0]
                tmpList.extend(tmp[1])
            self.stfLi[index] = [tmpList, self.stfLi[index][1], sort]
            index = index + 1
        self.stfLi.sort(key=self.getIndex)
    
    def lookUpENDict(self, s):
        string = s.lower()
        for pat, val in jobDictEN.items():
            if re.match(pat, string):
                return val
        return string.capitalize()

    def staffParse(self, jobStr):
        indexSet = set()
        extraList = []
        tmpEn = ''
        tmpZh = ''
        index = 0
        dic = jobDictZH
        while index < len(jobStr):
            if re.match('[a-zA-Z]', jobStr[index]):
                if tmpZh != '':
                    extraList.append(tmpZh)
                    tmpZh = ''
                tmpEn = tmpEn + jobStr[index]
                index = index + 1
                while index < len(jobStr) and re.match('[a-zA-Z]', jobStr[index]):
                    tmpEn = tmpEn + jobStr[index]
                    index = index + 1
                num = self.lookUpENDict(tmpEn)
                if type(num) == int:
                    indexSet.add(num)
                else:
                    extraList.append(num)
            else:
                path = dic.get(jobStr[index], 'default')
                if type(path) == int:
                    if tmpZh != '':
                        extraList.append(tmpZh)
                        tmpZh = ''
                    indexSet.add(path)
                    dic = jobDictZH
                    index = index + 1
                        
                elif type(path) == dict:
                    if tmpZh != '':
                        extraList.append(tmpZh)
                        tmpZh = ''
                    dic = path
                    index = index + 1
                    
                elif path == 'default':
                    if type(dic['default']) == int:
                        if tmpZh != '':
                            extraList.append(tmpZh)
                            tmpZh = ''
                        indexSet.add(dic['default'])
                        dic = jobDictZH
                        
                    elif dic['default'] == '+':
                        tmpZh = tmpZh + jobStr[index-1]
                        dic = jobDictZH
                        
                    else:
                        tmpZh = tmpZh + jobStr[index]
                        index = index + 1
                        dic = jobDictZH
        
        path = dic['default']
        if type(path) == int:
            indexSet.add(path)
        elif path == '+':
            tmpZh = tmpZh + jobStr[index-1]
        if tmpZh != '':
            extraList.append(tmpZh)
            
        indexList = list(indexSet)
        sortIndex = -6
        finalList = []
        if len(indexList) != 0:
            sortIndex = indexList[0]
            for item in indexList:
                finalList.append(jobList[item])
        finalList.extend(extraList)
        return [sortIndex, finalList]
                        
    def compose(self):
        if len(self.stfLi) == 1:
            print("未提取到有效信息")
            return
        print ("""{{Vocaloid_Songbox_Introduction
|bgcolor = #000
|ltcolor = #FFF""")
        index = 0
        while index < len(self.stfLi):
            print("|group" + str(index + 1) + " = " + "<br />".join(self.stfLi[index][0]))
            print("|list" + str(index + 1) + " = " + "<br />".join(self.stfLi[index][1]))
            index = index + 1
        print("}}")
        return
    
    def partternMaker(self):
        if self.divide['ch'] == []:
            return '[' + word + "".join(self.divide['hh'])\
            + ']+ ?[' + "".join(self.divide['hc'])\
            + '] ?[' + word + "".join(self.divide['cc'])\
            + ']+(?!' + "|".join(divide['hc']) + ')'
        else:
            return '[' + word + "".join(self.divide['hh'])\
            + ']+ ?[' + "".join(self.divide['hc'])\
            + '] ?[' + word + "".join(self.divide['cc'])\
            + ']*[^' + "".join(divide['ch']) + ']'
        
        
def getData(bbid):
    try:
        response = requests.get('https://api.bilibili.com/x/web-interface/view?aid=' + bbid)
    except:
        return '{"code":-1,"message":"网络异常，请重试。","data":{"title":"", "desc":""}}'
    return response.text



while (1):
    print("正在连接到神经网络...")
    #初始化检查网络信息
    testIof = json.loads(getData("6009789"))
    if testIof['code'] == -1:
        input("连接失败，请按任意键重连...\n")
        continue
    else:
        print("已成功连接到神经网络")
        break

while (1):
    bbid = input("操作菜单\n\
纯数字 ---- 解析视频简介\n\
　　Ｆ ---- 读取文件\n\
　　Ｅ ---- 退出程序\n")
    if bbid == 'E':
        print ("退出程序")
        break
    if bbid == 'F':
        print ("敬请期待")
        continue
    if bbid.isnumeric() == False:
        print("非法的输入")
        continue
    jsontype = json.loads(getData(bbid))
    if jsontype['code'] != 0:
        print ("Error", jsontype['code'], jsontype['message'])
        continue
    else:
        print (jsontype['data']['title'])
        intro = Intro(jsontype['data']['desc'], divide)
        intro.compose()
