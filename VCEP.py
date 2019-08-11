# -*- coding: utf-8 -*-
"""
@name: VOCALOID™ of Chinese Moegirlpedia™ Editor Plus
@author: Transentropy
@version: Beta 1.0
@source: https://github.com/transentropy/VCEP
"""

import json
import re
import time
import requests
from html import unescape

word = '-\u4e00-\u9fa5_.@a-zA-Z0-9\u3040-\u309f\u30a0-\u30fa'
url = 'http(s)?:\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?'
aid = 'av[0-9]+'

vLis = ['洛天依', '言和', '心华', '乐正绫', '星尘',
        '乐正龙牙', '初音未来', '墨清弦', '徵羽摩柯']
vDic = {'洛':0, '依':0, '南':0, '言':1, '心':2, '绫':3, '北':3,
        '星':4, '尘':4, '龙':5, '牙':5, '初':6, '葱':6, '墨':7,
        '弦':7, '摩':8, '柯':8}

divide = {"op":"",
          "ed":"",
          "ch":[],
          "hh":['/', '&'],
          'hc':[':', '：'],
          'cc':['/', '、', '&']
          }

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
           '歌':{'手': -2, '者': -2, 'default': -2},
           '协':{'力':-5, '助':-5, 'default':-5},
           '策':{'划':0, 'default':0},
           '呗':{'default':-2},
           '动':{'画':10, 'default':'+'},
           '贴':{'唱':5, 'default':'+'},
           '母':{'带':6, 'default':'+'},
           '出':{'品':-1, 'default':'+'},
           '封':{'面':9, 'default':9},
           '宣':{'传':-4, 'default':-4},
           '题':{'字':11, 'default':'+'},
           '美':{'工':13, 'default':'+'},
           'default':''
           }

jobDictEN = {'pv':10,
             '^mu':1,
             '^arr':2,
             'pro':2,
             '^comp':2,
             '^lyr':3,
             '^mix':5,
             '^thank':-3,
             '^spe':-3,
             '^vocal':-2,
             '^tu':4,
             '^illu':8,
             '^mov':10,
             'logo':12,
             }

pageFormat = """
{{{{Vocaloid_Songbox
|image = {title}.jpg
|图片信息 = 曲绘 by
|颜色 = 
|演唱 = {singers}
|歌曲名称 = {title}
|P主 = [[{up}]]
|bb_id = av{aid}
|投稿时间 = {date}{extra}
|再生 = {{{{bilibiliCount|id={aid}}}}}
}}}}

== 简介 ==
《'''{title}'''》是[[{up}]]于{date}投稿至[[bilibili]]的[[Vocaloid]]中文{origin}歌曲，由{singers}演唱{series}{album}。截至现在已有{{{{bilibiliCount|id={aid}}}}}次观看，{{{{bilibiliCount|id={aid}|type=4}}}}人收藏。

== 歌曲 ==
{{{{BilibiliVideo|id={aid}}}}}

== 歌词 ==
{staff}
<poem>
</poem>
"""

class Intro:
    def __init__(self, text, divide):
        self.text = text
        self.divide = divide
        self.forbid = [["^http", "简介补充", "曲目类型", '本家$', '^原'], ["^http", "^av", "^www"]]
        self.pattern = re.compile(self.partternMaker())
        self.urls = []
        self.aids = []
        self.titles = []
        self.stfLi = self.extract(self.pre(self.text))
        self.autoCheck()
        self.autoParse()
        self.singers = self.singerCollect()
        
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
        
    def urlCollect(self, matched):
        self.urls.append(matched.group())
        return 'http'
    
    def aidCollect(self, matched):
        self.aids.append(matched.group())
        return 'av'
    
    def titleCollect(self, matched):
        self.titles.append(matched.group().strip('《》'))
        return ''
        
    def pre(self, text):
        return re.sub(url, self.urlCollect,
               re.sub(aid, self.aidCollect,
               re.sub("《.+?》", self.titleCollect,
               unescape(text))))
        #pat = re.compile(self.divide['op'] + "(.|\s)+" +self.divide['ed'])

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
            
    def extract(self, text):
        brickList = self.pattern.findall(text)
        staffList = []
        for row in brickList:
            staffList.append(re.split("[" + "".join(self.divide['hc']) + "]", row))
        index = 0
        while index < len(staffList):
            staffList[index] = [re.split("[" + "".join(self.divide['hh']) + "]",
                                staffList[index][0].strip(' ')),
                                re.split("[" + "".join(self.divide['cc']) + "]",
                                staffList[index][1].strip('@ '))]
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
    
    def singerCollect(self):
        for row in self.stfLi:
            if '演唱' in row[0]:
                return row[1]
        else:
            return []
                        
    def compose(self):
        if len(self.stfLi) == 0 :
            return "未提取到有效信息"
        para = """{{Vocaloid_Songbox_Introduction
|bgcolor = 
|ltcolor = #FFFFFF"""
        index = 0
        while index < len(self.stfLi):
            para = para + "\n|group" + str(index + 1) + " = " + "<br />".join(self.stfLi[index][0])\
            + "\n|list" + str(index + 1) + " = " + "<br />".join(self.stfLi[index][1])
            index = index + 1
        para = para + "\n}}"
        return para

def delString (text, a, b):#del a to b-1, a >= b return original string
    if a < b and a >= 0 and b <= len(text):
        return text[0:a] + text[b:len(text)]
    else:
        return text

class Song:
    def __init__(self, data):
        self.aid = data['aid']
        self.oriTitle = data['title']
        self.cover = data['pic']
        self.pubdate = data['pubdate'] + 28800 #UTC+8
        self.uploader = data['owner']['name']
        self.view = data['stat']['view']
        
        self.titleInfo = self.titleParser(self.oriTitle)
        self.introInfo = Intro(data['desc'], divide)
        
        if self.introInfo.singers != []:
            self.singers = self.introInfo.singers.copy()
        else:
            self.singers = self.titleInfo['singers']
            self.introInfo.singers = self.singers
            self.introInfo.appand([['演唱'], self.singers, 14])
        
    def getFormatTime(self, fm):
        if fm == 0:
            return time.strftime("%Y-%m-%d %H:%M", time.gmtime(self.pubdate))
        else:
            return time.strftime("%Y{y}%m{m}%d{d}",time.gmtime(self.pubdate))\
                                 .format(y='年', m='月', d='日')
    
    @classmethod
    def singerParser(cls, text):
        vDic = {'洛':0, '依':0, '南':0, '言':1, '心':2, '绫':3, '北':3,
                '星':4, '尘':4, '龙':5, '牙':5, '初':6, '葱':6, '墨':7,
                '弦':7, '摩':8, '柯':8}
        singerSet = set()
        for char in text:
            tmp = vDic.get(char, None)
            if tmp != None:
                singerSet.add(tmp)
        
        return singerSet
    
    @classmethod                             
    def titleParser(cls, text):
        infoDict = {'title':'', 'origin':1, 'singers':[],
                    'series':'', 'album':'', 'other':[]}
        symbols = {'op':'【[（(', 'clz':'】]）)', 'top':'《', 'tclz':'》',
                   'divide':'/，,+&︱、×'}
        tmp = ''
        tmpTitles = []
        flags = 0
        index = 0
        l = len(text)
        
        while (index < l):
            char = text[index]
            if char in symbols['op']:
                if len(tmp) != 0:
                    if flags == 0:
                        tmpTitles.append(tmp)
                    else:
                        infoDict['other'].append(tmp)
                tmp = ''
                flags = flags + 1
                index = index + 1
                continue
            if char in symbols['clz']:
                if flags != 0:
                    if len(tmp) != 0:
                        infoDict['other'].append(tmp)
                    tmp = ''
                    flags = flags - 1
                index = index + 1
                continue
            tmp = tmp + char
            index = index + 1
            
        if len(tmp) != 0:
            if flags == 0:
                tmpTitles.append(tmp)
            else:
                infoDict['other'].append(tmp)
                
        singerSet = set()
        
        if len(tmpTitles) > 0:
            tmpLi = re.split("[—-]+|[Ff]eat.|by", tmpTitles[0])
            infoDict['title'] = tmpLi[0]
            for item in tmpLi:
                title = re.search('《.+》', item)
                if title:
                    infoDict['title'] = title.group().lstrip('《').rstrip('》')
                    if title.span()[0] > 0:
                        infoDict['other'].append(item[:title.span()[0]])
                    if title.span()[1] < len(item):
                        infoDict['other'].append(item[title.span()[1]:])
                else:
                    infoDict['other'].append(item.strip(" "))
            
            for i in tmpTitles[1:]:
                infoDict['other'].append(i.strip(" "))
                
        
        for item in infoDict['other']:
            if item.find("翻唱") != -1\
            or item.find("填词") != -1\
            or item.lower().find("cover") != -1:
                infoDict['origin'] = 0
            series = re.search(".+(系列|[p|P]roject)", item)
            if series:
                infoDict['series'] = series.group().strip(" ")
            album = re.search('[《『].+[》』]', item)
            if album:
                infoDict['album'] = album.group().lstrip('《『').rstrip('》』')
            else:
                album = re.search("(?<=辑).+(?=收录)", item)
                if album:
                    infoDict['album'] = album.group()
            tmpSet = cls.singerParser(item)
            if len(tmpSet) > len(singerSet):
                singerSet = tmpSet.copy()
                
        for i in singerSet:
            infoDict['singers'].append(vLis[i])
        
        return infoDict
    
    def compose(self):
        origin = ["'''翻唱'''", "原创"][self.titleInfo['origin']]
        album = self.titleInfo['album']
        if album != '':
            extra = "\n，收录于专辑《" + album + '》'
            album = "，专辑《" + album + "》的收录曲"
        else:
            extra = ''
        series = self.titleInfo['series']
        if series != '':
            series = '，为' + series + '第 作'
        text = pageFormat.format(title=self.titleInfo['title'],
                                 aid=self.aid,
                                 up=self.uploader,
                                 date=self.getFormatTime(1),
                                 singers="[[" + "]]、[[".join(self.singers) + "]]",
                                 origin=origin,
                                 album=album,
                                 series=series,
                                 extra=extra,
                                 staff=self.introInfo.compose())
        for s in self.singers:
            text = text + ('\n{{' + s + '|collapsed}}')
        
        text = text + ('\n[[Category:中国音乐作品]]\n[[Category:使用VOCALOID的歌曲]]')
        for s in self.singers:
            text = text + ('\n[[分类:' + s + '歌曲]]')
            
        return text

def getData(bbid):
    try:
        response = requests.get('https://api.bilibili.com/x/web-interface/view?aid=' + bbid)
    except:
        return '{"code":-1,"message":"网络异常，请重试。","data":{"title":"", "desc":""}}'
    return response.text    

if __name__=="__main__":
    print ("""VOCALOID™ of Chinese Moegirlpedia™ Editor Plus (Beta 1.0)
Pover by Transentropy©
GET UPDATED: github.com/transentropy/VCEP\n""")
    
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
    
    file = open("page.txt", 'a')
    while (1):
        bbid = input("\n请输入AV号，按回车确定；直接回车退出程序\n")
        if bbid == '':
            break
        if bbid.isnumeric() == False:
            print("非法的输入")
            continue
        videoInfo = json.loads(getData(bbid))
        if videoInfo['code'] != 0:
            print ('Error ' + str(videoInfo['code']) + '：' + videoInfo['message'])
            continue
        
        mainSong = Song(videoInfo['data'])
        print ("正在解析", mainSong.oriTitle, "……")
        wikiText = mainSong.compose()
        print ("---------------------------")
        print (wikiText)
        file.write(wikiText)
        file.write("\n\n------------------------------------------------------\n")
        print ("---------------------------\n解析完成，生成文本已写入文件 page.txt")
        file.flush()
        
    file.close()
    