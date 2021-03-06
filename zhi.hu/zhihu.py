#!/usr/bin/python
import urllib2, json, re, os, time,HTMLParser,eml,datetime
from lxml import etree
url = """http://www.zhihu.com/people/yu-xiao-wei-71-85"""
#url = """http://www.zhihu.com/people/starfire"""
header = {}
html_parser = HTMLParser.HTMLParser()
def TZ_Tran(TimeStamp):
	class GMT8(datetime.tzinfo):
		def utcoffset(self, dt):
			return datetime.timedelta(hours=8) + self.dst(dt)
		def dst(self, dt):
			return datetime.timedelta(0)
		def tzname(self,dt):
			return "GMT +8"
	return str(datetime.datetime.fromtimestamp(TimeStamp,tz=GMT8()))
def Get_Acti(content):
	code = content.decode('utf-8', 'ignore')
	page = etree.HTML(code)
	Target = page.xpath(u"/html/body/div[@class='zg-wrap zu-main']/div[@class='zu-main-content']/div[@class='zu-main-content-inner']/div[@class='zm-profile-section-wrap']/div[@class='zm-profile-section-list profile-feed-wrap']/div['zh-profile-activity-page-list']")
	JSON_Arr = []
	for i in Target[0]:
		flag = False
		content = i.xpath(u"div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']")
		TS = int(i.attrib['data-time'])
		T= TZ_Tran(TS)
		Data =  content[0].xpath(u'a')
		Type = "focus a "+re.split("/",Data[1].attrib['href'])[1]
		if 'title' in Data[1].attrib:
			qus = Data[1].attrib['title']
		else:
			qus = Data[1].text
		if i.attrib['data-type'] == 'a':
			Type = "agree an answer in"
			flag = 2
		if len(content[0].xpath(u'a'))>2:
			Type = "answer a question"
			qus = Data[2].text
			flag = 3
		ans = ""
		if flag:
			ans = i.xpath(u"div[@class='zm-item-answer ']/div[@class='zm-item-rich-text']/textarea")[0].text
		JSON_Arr.append( {"TimeStamp":TS,"Time":T,"Type":Type,"Question":qus,"Answer":ans})
	return JSON_Arr
def GetNew():
	request = urllib2.Request(url,headers=header)
	return urllib2.urlopen(request).read()
Arr = Get_Acti(GetNew())
DB = os.listdir(os.path.split(os.path.realpath(__file__))[0]+"/DB")
MsgQuene = []
for i in Arr:
	if (str(i["TimeStamp"])+".json" not in DB) :
		f = open(os.path.split(os.path.realpath(__file__))[0]+"/DB/%s.json"%(i["TimeStamp"]),"w")
		f.write(json.dumps(i))
		f.close()
		MsgQuene.append(i)
for i in MsgQuene:
	if eml.send_mail(["admin@nkucodingcat.com"],"SomeOne "+i["Type"]+" "+i["Question"],"It happened @ "+str(i["Time"])+"\n"+re.sub("\<br\>","\n",i["Answer"])):
	#if 1:
		print "Mail Sent"
	else:
		print "Mail Sent Error"