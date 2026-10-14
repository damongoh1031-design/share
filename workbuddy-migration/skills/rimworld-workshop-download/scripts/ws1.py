# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, re, sys
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"}
def fetch(q,num=30):
    url=("https://steamcommunity.com/workshop/browse/?appid=294100&searchtext="+urllib.parse.quote(q)+
         "&browsesort=textsearch&section=readytouseitems&numperpage=%d"%num)
    h=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read().decode("utf-8","ignore")
    return [(m.group(1),m.group(3)) for m in re.finditer(r'\\"publishedfileid\\":\\"(\d+)\\"(.*?)\\"title\\":\\"(.*?)\\"',h)]
for q in sys.argv[1:]:
    print("### %s"%q)
    try:
        for wid,t in fetch(q)[:8]: print("   %-12s %s"%(wid,t))
    except Exception as e: print("   ERR",e)
