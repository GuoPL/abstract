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
the method based on Motif for abstract extraction
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
from optparse import OptionParser
reload(sys)
sys.setdefaultencoding('utf8')

def readdata(file,delimiter,index):
    for line in file:
	y1=[]
#	y=line.strip().split('\001')[0].encode('utf-8').split('。')
	y=line.strip().split(delimiter[0])[index].split(delimiter[1])
#	yield y

	for ele in y:
		y1 += ele.split(delimiter1[2]) 
	yield y1
#	yield line.strip().split('\001')[0]

def getdata(filename,delimiter,index):
    file = codecs.open(filename,'r','utf-8')
    data = list(readdata(file,delimiter,index))
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
		dic_M3[i]=len(set(M3[:len_A])&set(article[i]))
		dic_M4[i]=len(set(M3[:len_A])&set(article[i]))

	Mr3= sorted(dic_M3.iteritems(), key=lambda x:x[1], reverse=True)
	Mr4= sorted(dic_M4.iteritems(), key=lambda x:x[1], reverse=True)

	temp=[source[key[0]] for key in Mr3][:len_A]
	tem=[source[key[0]] for key in Mr4][:len_A]

	hah= ('，'.join(temp)).split('，')

	dic_M31,dic_M41={},{}
	for i in xrange(len(hah)):
		dic_M31[i]=len(set(M3)&set(hah[i]))
		dic_M41[i]=len(set(M3)&set(hah[i]))

	Mr31= sorted(dic_M31.iteritems(), key=lambda x:x[1], reverse=True)
	Mr41= sorted(dic_M41.iteritems(), key=lambda x:x[1], reverse=True)

	temp1=[hah[key[0]] for key in Mr31][:len_A]
	tem1=[hah[key[0]] for key in Mr41][:len_A]
	
	return temp1,tem1
	
def getStop(stopwordFile):
	fil=codecs.open(stopwordFile,'r','utf-8')
	stop=[]
	for line in fil:
		stop.append(line.strip())
	return stop

def main(fi,fo,stopwordFile,delimiter,index,L,m,n,len_A):
	data_source=getdata(filename_source,delimiter,index)	
	stop=getStop(stopwordFile)
	fo=open(fo,'w')
	for i in xrange(len(data_source)):
		test= set(jieba.cut(data_source[i][0]))
		data=[list(set(jieba.cut(ele))-set(stop)) for ele in data_source[i]]
		network_dic=createNetworkDic(data,n,m)
		M3=getMotifWord(findMotif300(network_dic),L)
		M4=getMotifWord(findMotif400(network_dic),L)
		if M3:
			A3,A4=get_abstract(M3,M4,data,data_source[i],len_A)
			fo.write('。'.join(A3))

	fo.close()
 
if __name__ == "__main__":
	
	parser=OptionParser(usage="%prog -d fi -o fo -w stopwordFile -s delimiter -i index -l L -m m -n n -len len_A")

	parser.add_option(
		"-d","--fi",
		help=u"the input path"
	)

	parser.add_option(
		"-o","--fo",
		help=u"the output path"
	)

	parser.add_option(
		"-w","--stopwordFile",
		help=u"the stopwordFile path"
	)

	parser.add_option(
		"-s","--delimiter",
		help=u"the delimiter list, the first is the delimiter between the columns, the second and third is the article's delimiter"
	)

	parser.add_option(
		"-i","--index",
		help=u"the array of the index in content, which need to be solved"
	)

	parser.add_option(
		"-l","--L",
		help=u"the topK keyword, which will be used to decide the rank of sentence"
	)

	parser.add_option(
		"-m","--m",
		help=u"the threshold"
	)

	parser.add_option(
		"-n","--n",
		help=u"the window length"
	)

	parser.add_option(
		"-len","--len_A",
		help=u"the number of the sentence we need"
	)

	if not sys.argv[1:]:
		parser.print_help()
		exit(1)

	(opts,args) = parser.parse_args()
	main(fi=opts.fi,fo=opts.fo,stopwordFile=opts.stopwordFile,delimiter=opts.delimiter,index=opts.index,L=opts.L,m=opts.m,n=opts.n,len_A=opts.len_A)






	
