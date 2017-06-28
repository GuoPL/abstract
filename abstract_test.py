# -*- coding: utf-8 -*-
#!/usr/bin/env python
# coding=utf-8
#
# Copyright @2017 R&D
#
# Author: PeilunGuo <guopeilun123@gmail.com>
#
# 2017/3/13 2017/3/17
#

'''
test the method based on Motif for abstract extraction
'''
import os
import codecs
from textrank4zh import TextRank4Keyword,TextRank4Sentence
from snownlp import SnowNLP
import jieba.analyse
import time
import networkx as nx
from itertools import combinations
from collections import Counter
import sys
import chardet
import re
reload(sys)
sys.setdefaultencoding('utf8')

def getDeli():
	de=file('delimiter.txt','r')
	return de.readline().strip()

def readdata(file):
    for line in file:
#	y1=[]
#	y=line.strip().split('\001')[0].encode('utf-8').split('。')

#	for ele in y:
#		y1 += ele.split('，') 
#	yield y
#	yield line.strip().split('\001')
#	yield line.strip().split('。')
	yield line.strip().split('\001')[0].split('。')

def getdata(filename):
    file = codecs.open(filename,'r','utf-8')
    data = list(readdata(file))
    file.close()
    return data

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
		for i in xrange(len(network_dic[key])-1):
			for j in xrange(i+1,len(network_dic[key])):
				for k in network_dic[network_dic[key][i]]:
					if k in network_dic[network_dic[key][j]] and k != key:
						mot400.append([key,network_dic[key][i],network_dic[key][j],k])	
	return mot400
		
def findMotif300(network_dic):
	mot300=[]
	for key in network_dic.keys():
		for i in xrange(0,len(network_dic[key])-1):
			for j in xrange(i+1,len(network_dic[key])):
				if network_dic[key][i] in network_dic and network_dic[key][j] in network_dic[network_dic[key][i]]:
					mot300.append([key,network_dic[key][i],network_dic[key][j]])
				elif network_dic[key][j] in network_dic and network_dic[key][i] in network_dic[network_dic[key][j]]:
					mot300.append([key,network_dic[key][j],network_dic[key][i]])
	return mot300
				
def getMotifWord(mot,L):
	Mword,dic_m=[],{}
	for ele in mot:
		for el in ele:
			Mword.append(el)
	for ele in Mword:
		dic_m[ele]=dic_m.setdefault(ele,0)+1
	dic=dict(sorted(dic_m.items(), lambda x,y: cmp(x[1],y[1]), reverse=True))
	return dic.keys()[:L]
	
def getkeywordz(eli,topK):
	tags=[]
	tr4w=TextRank4Keyword()
	tr4w.analyze(text=eli, lower=True, window=2)
	keyword=tr4w.get_keywords(topK,word_min_len=1)
	for item in keyword:
		tags.append(item.word)
	return tags

def getkeywordj(eli,topK):
	tags=jieba.analyse.extract_tags(eli,topK)
	return tags

def getoverlap(LK,Ll,sh):
	try:
        	R=sh/float(LK)
        	P=sh/float(Ll)
		return 2*R*P/(R+P)
	except:
		return 0.0

def add(a,b):
	return a+b

def trans(word):
    word=word.lower()
    return [word[:-1],word,word+'s']

def getF(K,label):
    labe=label.split(';')
    num = 0.0
    for i in xrange(len(labe)):
        lab=labe[i].split(' ')
        temp=0
        for ele in lab:
            word=trans(ele)
            if set(word)&set(K):
                temp += 1
        if temp==len(lab):
            num += 1
    return getoverlap(len(K),len(label),num)

def getF_all(elem,n,m,L):
    network_dic=createNetworkDic(elem[0],n,m)
    M3=getMotifWord(findMotif300(network_dic),L)
    M4=getMotifWord(findMotif400(network_dic),L)
    KJ=getkeywordj(elem[0],L)
    KZ=getkeywordz(elem[0],L)

    return M3,M4

def get_abstract(M3,M4,article,source,len_A):
	dic_M3,dic_M4={},{}
	for i in xrange(len(article)):
		dic_M3[i]=len(set(M3)&set(article[i]))
		dic_M4[i]=len(set(M3)&set(article[i]))

	Mr3= sorted(dic_M3.iteritems(), key=lambda x:x[1], reverse=True)
	print ' '.join(M3)
	print Mr3
	Mr4= sorted(dic_M4.iteritems(), key=lambda x:x[1], reverse=True)

	temp=[source[key[0]] for key in Mr3][:len_A]
	tem=[source[key[0]] for key in Mr4][:len_A]
	return temp,tem
	
def getStop():
	fil=codecs.open('../../stopword.txt','r','utf-8')
	stop=[]
	for line in fil:
		stop.append(line.strip())
	return stop

def main():
#	data=getdata(filename)
	data_source=getdata(filename_source)	
	stop=getStop()
	for L in xrange(5,21,5):
		for i in xrange(len(data_source)):
			test= set(jieba.cut('。'.join(data_source[i])))
			data=[list(set(jieba.cut(ele))-set(stop)) for ele in data_source[i]]
#			data_s=[]
#			for ele in data_source[i]:
#				data_s+=ele.split('，')
			ti=time.clock()
			network_dic=createNetworkDic(data,n,m)
			M3=getMotifWord(findMotif300(network_dic),L)
			M4=getMotifWord(findMotif400(network_dic),L)
			if M3:
				A3,A4=get_abstract(M3,M4,data,data_source[i],len_A)
				ti1=time.clock()
				t=ti1-ti

				tt1=time.clock()
				tr4s=TextRank4Sentence()
#				tem='。'.join(data_source[i])
#				print chardet.detect(tem)
				s=SnowNLP('。'.join(data_source[i]))
				TA=s.summary(len_A)
				tt2=time.clock()
				tt=tt2-tt1

				print '#'.join(A3)
				print '$'.join(A4)

				print 'T'.join(TA)
				print t
				print tt
				print '!!!!!!!!!!!!!!!!'
				print ' '.join(s.keywords(3))
				print '。'.join(data_source[i])
				break
			print 1
		break
 

#filename_source='163-2.txt'
filename_source='three.txt'
#filename_source='163_c.txt'
#fo=open('result_test.txt','w')
m=4
n=20
len_A=2
main()
#fo.close()
print 'finished'

