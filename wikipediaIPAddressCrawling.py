from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import random
import re
import json
from urllib.parse import urlparse

def getLinks(articleUrl):
	html = urlopen("http://en.wikipedia.org"+articleUrl)
	bsObj = BeautifulSoup(html,"lxml")
	return bsObj.find("div",{"id":"bodyContent"}).findAll("a",href = re.compile("^(/wiki/)((?!:).)*$"))

def getHistoryIPs(pageUrl):
	pageUrl = pageUrl.replace("/wiki/","")
	historyUrl = "http://en.wikipedia.org/w/index.php?title="+pageUrl+"&action=history"
	print("history url is: "+ historyUrl)
	html = urlopen(historyUrl)
	bsObj = BeautifulSoup(html,"html.parser")
	ipAddresses = bsObj.findAll("a",{"class":"mw-anonuserlink"})
	addressList = set()
	for ipAddress in ipAddresses:
		addressList.add(ipAddress.get_text())
	return addressList

def getCountry(ipAddress):
	response = urlopen("http://freegeoip.net/json/"+ipAddress).read().decode('utf-8')
	responseJson = json.loads(response)
	return responseJson.get("country_code")


random.seed(datetime.datetime.now())
countryDictionary={}
countryUrl = urlopen("http://www.benricho.org/translate/countrycode.html")
bsObjForCountry = BeautifulSoup(countryUrl,"lxml")
a = bsObjForCountry.findAll("img",{"src": re.compile("^(img/)((?!:).)*(\.png)$")})
for x in a:
	div = x.parent.parent.find("div",{"align":"center"})
	if div==None:
		countryDictionary.update({"CW":x.parent.get_text()})
	else:
		if x.parent.find("div",{"style":"display:none"}) != None:
			countryDictionary.update({div.get_text():list(x.parent.children)[2]})
		else:
			countryDictionary.update({div.get_text():x.parent.get_text()})

def process():
	print("使用方法：Wikipediaで気になるWebsiteのアドレスを入力してください。")
	print("その後、そのページの全てのリンクに対して、更新した人のIPアドレスと国コードと国名を表示します。")
	inputOfWebsite = input()
	while urlparse(inputOfWebsite).path.find('/wiki/') == -1:
		print("WikipediaのURL形式になっていません。もう一度入力してください：")
		inputOfWebsite = input()
	
	links = getLinks(urlparse(inputOfWebsite).path)
	
	while(len(links)>0):
		for link in links:
			print("--------------------------------------")
			historyIPs = getHistoryIPs(link.attrs['href'])
			for historyIP in historyIPs:
				countryCode = getCountry(historyIP)
				print(historyIP,countryCode,countryDictionary.get(countryCode))
			
		newLink = links[random.randint(0,len(links)-1)].attrs['href']
		links = getLinks(newLink)

process()
