# -*- coding: utf-8 -*-
#!/usr/bin/env python
# coding=utf-8
#
# Copyright @2017 R&D
#
# Author: PeilunGuo <guopeilun123@gmail.com>
#
# 2017/3/13 2017/3/17 2020/03/03
#

'''
test the method based on Motif for abstract extraction
'''
import codecs
from textrank4zh import TextRank4Keyword,TextRank4Sentence
from snownlp import SnowNLP
import time
from itertools import combinations
import re


def Spllist(lis,n):
    l = list(lis[i:i+n] for i in xrange(0,len(lis),n/2))
    return l

def Comlist(lis):
    l = []
    for ele in combinations(lis,2):
        l.append(ele)
    return l

def GetTop(Dict,k):
    Dic={}
    for item in [i for i in Dict.items() if i[1]>k]:
        Dic[item[0]]=item[1]
    return Dic

def Getdict(ele,n,k): 
    dic={}
#    li = Spllist(' '.join(ele),n) 不按句子分, 自定义长度构建网络
    for item in ele:
        li = Comlist(item)
        for el in li:
            dic[el]=dic.setdefault(el,1)+1
    di = GetTop(dic,k)
    return di

def getedge(con,n,k):
    list_edge=[]
    dic = Getdict(con,n,k)
    for ele in dic.keys():
        list_edge.append(ele)
    return list_edge

def createNetworkDic(con,n,k):
    network_dic={}
    list_edge=getedge(con,n,k)
    for ele in list_edge:
        if ele[0] in network_dic:
            if ele[1] in network_dic[ele[0]]:
                continue
            else:
                network_dic[ele[0]].append(ele[1])
        else:
            network_dic.setdefault(ele[0],[ele[1]])

        if ele[1] in network_dic:
            if ele[0] in network_dic[ele[1]]:
                continue
            else:
                network_dic[ele[1]].append(ele[0])
        else:
            network_dic.setdefault(ele[1],[ele[0]])
    return network_dic

def findMotif400(network_dic):
    mot400=[]
    for key in network_dic.keys():
        for i in range(len(network_dic[key])-1):
            for j in range(i+1,len(network_dic[key])):
                for k in network_dic[network_dic[key][i]]:
                    if k in network_dic[network_dic[key][j]] and k != key:
                        mot400.append([key,network_dic[key][i],network_dic[key][j],k])    
    return mot400
        
def findMotif300(network_dic):
    mot300=[]
    for key in network_dic.keys():
        for i in range(0,len(network_dic[key])-1):
            for j in range(i+1,len(network_dic[key])):
                if network_dic[key][i] in network_dic and network_dic[key][j] in network_dic[network_dic[key][i]]:
                    mot300.append([key,network_dic[key][i],network_dic[key][j]])
                elif network_dic[key][j] in network_dic and network_dic[key][i] in network_dic[network_dic[key][j]]:
                    mot300.append([key,network_dic[key][j],network_dic[key][i]])
    return mot300
                
def getMotifWord(mot,keywords_num):
    Mword,dic_m=[],{}
    for ele in mot:
        for el in ele:
            Mword.append(el)
    for ele in Mword:
        dic_m[ele]=dic_m.setdefault(ele,0)+1
    dic=list(sorted(dic_m.items(), key=lambda x: x[1], reverse=True))
    return dic[:keywords_num]

def get_abstract(M,article,source,len_A):
    dic={}
    for i in range(len(article)):
        dic[i]=len(set(M)&set(article[i]))

    Mr= sorted(dic.items(), key=lambda x:x[1], reverse=True)

    temp=[source[key[0]] for key in Mr][:len_A]
    return temp
    
def getStop():
    fil=codecs.open('./stopword.txt','r','utf-8')
    stop=[]
    for line in fil:
        stop.append(line.strip())
    return stop

def main():
    p = re.compile(r'。！？\s+') #划分句子的分割符
    text = """菲利普·克莱因(Philippe Klein)，一位目前仍在武汉工作的法国全科医生。 菲利普·克莱因(Philippe Klein)，一位目前仍在武汉工作的法国全科医生。去年12月，武汉出现新型冠状病毒感染肺炎疫情，随形势发展愈加严峻，在汉工作生活的许多法国公民相继离去，克莱因却毅然决定留下来。中新社记者 张畅 摄 　　在其位于汉阳区住所，数只封上口的黑色塑料袋堆于门前等待回收，里面装着克莱因这>      些天使用过的防护衣和口罩；医疗物资摊放屋内走廊两侧，空荡的厨房酒吧台上一瓶未开封的法国香槟格外显眼。 在其位于汉阳区住所里医疗物资摊放屋内走廊两侧，空荡的厨房酒吧台上一瓶未开封的法国香槟格外显眼。>      中新社记者 杨程晨 摄 　　“买好这瓶酒就放在那，等这场疫情结束我的太太回到身边，与她一同打开庆祝。”近日，中新社记者赴约对克莱因专访。目前，他的妻子身在法国，正等待疫情远去回武汉团聚。 　　去年12月，
      武汉出现新型冠状病毒感染肺炎疫情。随形势发展愈加严峻，在汉工作生活的许多法国公民相继离去。克莱因却毅然决定留下来。 　　“回到法国我什么也干不了，我是一名医生，武汉是我工作的地方。”他透露，实际上，>      因各式原因留汉的外籍人士还有相当数量。 资料图为菲利普·克莱因(左一)与同事们在门诊。中新社发 菲利普·克莱因 供图 　　来武汉工作6年，这位全科医生任职武汉协和医院的国际门诊部，主要为在汉外籍人士提供服>      务。疫情发生以来，为防止交叉感染，该医院国际门诊暂停营业。 　　但克莱因并未放假，而是每日穿戴整套防护装备自驾往返武汉三镇，在中国同事的线上协助下为有需要的外籍人士上门看诊。 　　每日接触各式疾病及
      病患，克莱因清楚新型肺炎的危险性。“在此工作既是职责所在，也是职业要求。即使这份工作只是抗击疫情战线上的一个小岗位，那也是我所能做的支持武汉市民撑下去的一种方式。” 　　“武汉是一座大城市，经过了这些
      年努力也正在成为一座越来越好的城市。”第一次看到不明原因肺炎在武汉被发现的消息，克莱因首先想到，“接下来全世界都要开始关注和议论武汉了。疫情对我来说，是一件难过的事”。 克莱因说 “买好这瓶酒就放在那，
      等这场疫情结束我的太太回到武汉，与她一同打开庆祝。图为菲利普·克莱因在挂着红灯笼的家门口。中新社记者 张畅 摄 　　他说，武汉1月23日“封城”后，外籍人士中间出现了一定程度的担心情绪，但大部分人都遵照有>      关部门安全建议留在住所内。直到现在，武汉虽然还处在特殊时期，在汉外国人也没有担心基本生活供应。 　　克莱因近些天所遇见的外籍人士“并没有恐慌情绪”。他说，人口超千万的城市“封城”史所罕见，政府作此决定>      需要很大勇气。在质疑声中进行决策是困难且复杂的，事实证明关闭离汉通道后，新冠病毒向外传播速度明显减缓。 　　“关于这次新病毒，人类所知甚少，我们现在能做的只有等待、耐心地等待。”聊天的过程，克莱因不>      断强调希望在困难时刻多发出一些积极的声音，“这是我面对人生困境的方式”。 菲利普·克莱因接受中新社记者专访。中新社记者 张畅 摄 　　他提到，许多专家学者正在夜以继日地投入工作，中国科学家对于新型肺炎的>      认知进度要远快于17年前认识“非典”。中国其他省份乃至世界多个国家已向湖北伸出援手，相信不管是医疗物资还是医护人员的紧缺都是暂时的。 　　克莱因同时指出，导致新型肺炎这一级别疫情发生因素有很多。通过应>      对突发性公共卫生事件，武汉完全可以借此机会积攒城市治理上的诸多经验并为未来加以运用。对于从立法根源层面解决非法贩卖野生动物等问题，他亦表示正逢其时。 　　采访结束，克莱因与记者在社区门口道别，转过>      身去已近傍晚。他再一次迅速备好应急装备前往武昌，服务当天的最后一位病患"""
    article = re.split(p, text)
    stop=getStop()
    data=[list(set(jieba.cut(ele))-set(stop)) for ele in article]
#        ti=time.clock()
    network_dic=createNetworkDic(data,n,m)
    M3=getMotifWord(findMotif300(network_dic),keywords_num = 20) #M3性能好，效果也不错
#    # keywords_num：提取的关键词数量，基于这些关键词衡量每个句子的重要性
#    print(M3) #输出基于M3提取的关键词
#    M4=getMotifWord(findMotif400(network_dic),keywords_num = 20)  #M4相对M3性能较差，但是效果相对较好。
#    print(M4) #输出基于M4提取的关键词
    if M3:
        A3=get_abstract(M3,data,article,len_A)
        print ('#'.join(A3))
#        A4=get_abstract(M4,data,article,len_A)
#        print ('$'.join(A4))

#                ti1=time.clock()
#                t=ti1-ti
#
#                tt1=time.clock()
#                tr4s=TextRank4Sentence()
##                tem='。'.join(data_source[i])
##                print chardet.detect(tem)
#                s=SnowNLP('。'.join(data_source[i]))
#                TA=s.summary(len_A)
#                tt2=time.clock()
#                tt=tt2-tt1

m=4 #构建的网络的边的阈值
n=20 #基于长度构建网络的边界
len_A=2 #提取句子的数量
main()
#fo.close()
print ('finished')