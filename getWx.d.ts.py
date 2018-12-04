# -*- coding: utf-8 -*-
import requests
import sys  
import os
import time
import urllib
import multiprocessing as mp
import thread

from bs4 import BeautifulSoup
# from requests.packages.urllib3.exceptions import InsecureRequestWarning,InsecurePlatformWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
# 不是接口，不能在客户端使用
NOT_METHOD_CLS   = 0
# 类 和 方法
CLS_METHOD   = 1
# 只有方法
ONLY_METHOD  = 2
# 类的属性
CLS_ATTR     = 3
# 方法的参数
METHOD_ARG   = 4
# 只有类
ONLY_CLS     = 5 
# 强制重新加载
FORCE_RELOAD_HTML = False

g_icout = 5;
g_index = {};
reload(sys)  
sys.setdefaultencoding('utf-8')   

requests.adapters.DEFAULT_RETRIES = 5
requests.packages.urllib3.disable_warnings()

def create_session():
    session = requests.session()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Host': 'developers.weixin.qq.com',
        'Referer': 'https://developers.weixin.qq.com'
    }
    r = session.get('https://developers.weixin.qq.com/minigame/dev/api/',headers = header,verify=False)
    # print r.status_code
    if not os.path.exists('page'):
        os.mkdir('page')
    with open('page/first.html', 'w') as fp:
        fp.write(r.content)
    return session,r.content

# 根据url来遍历
def get_evy_url(session,sts):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Host': 'developers.weixin.qq.com',
        'Referer': 'https://developers.weixin.qq.com'
    }
    x  = sts.split("/")
    if not FORCE_RELOAD_HTML and os.path.exists('page/%s'%(x[len(x)-1])):
        print "%s already exists"%x[len(x)-1][0:-5]

    r = session.get('https://developers.weixin.qq.com/minigame/dev/api/'+sts,headers = header,verify=False) # 实现验证码登陆
    if r.status_code == 200:
        with open('page/%s'%(x[len(x)-1]), 'w') as fp:
            fp.write(r.content)
    else:
        with open("error.txt","a+") as fp:
            fp.write('%s\n'%sts);

# 方法和参数
def wtMethod(method,args):
    if method[1] != None:
        return "%s(%s): %s"%(method[0],args,method[1])
    else:
        return "%s(%s)"%(method[0],args)

# 写文件
def writeFile2(acls):
    citext = ["interface","class"]
    # 用于记录需要写的内容
    writeContent = []
    
    # 先写只有函数的函数，比如 setTimeout
    for m in acls['m']:
        nstr = ""
        if len(m) == 3:
            for n in m[2]:
                if n['t'] == '':
                    nstr =  "%s,%s"%(nstr,n['n'])
                else:
                    nstr ="%s,%s: %s"% (nstr,n['n'],n['t'])
            
            nstr = nstr[1:len(nstr)]
        if nstr != "":
            writeContent.append('/**\n* %s \n*/\ndeclare function %s;\n'%(m[1],wtMethod(m[0],nstr)))

    clss = []
    for c in acls['c']:
        clss.append([c,acls['c'][c]])

    clss.sort(lambda x,y:len(x[1]['m']) -len(x[1]['m']))

    for m in clss:
        lenofA = len(m[1]['a'])

        if lenofA > 0:
            lenofA = 1
        # 判断类型是否没有属性存在
        writeContent.append('/**\n* %s \n*/\ndeclare %s %s{\n'%(m[1]['i'],citext[lenofA],m[0]))

        # 判断类型 有属性存在，则先把属性写在前面
        if lenofA > 0:
            ma = m[1]['a']
            for k in ma:
                if not isinstance(k,dict):
                    writeContent.append("\t%s:{\n"%k)
                    for a in ma[k]:
                        if a['r'] == '':
                            writeContent.append('\t\t/**\n\t\t* %s \n\t\t*/\n\t\t%s;\n' % (a['i'], a['a']))
                        else:
                            writeContent.append('\t\t/**\n\t\t* %s \n\t\t*/\n\t\t%s: %s;\n' % (a['i'], a['a'],a['r']))
                    writeContent.append("\t}")
                else:
                    a = k
                    if a['r'] == '':
                        writeContent.append('\t/**\n\t* %s \n\t*/\n\t%s;\n' % (a['i'], a['a']))
                    else:
                        writeContent.append('\t/**\n\t* %s \n\t*/\n\t%s: %s;\n' % (a['i'], a['a'],a['r']))

        # 开始写类的方法
        for mm in m[1]['m']:
            nstr = ""
            if len(mm) == 3:
                mb = mm[2]
                for n in mb:
                    if len(n['r_a']) == 0:
                        nstr = "%s,%s:%s"%(nstr,n['n'],n['t'])
                    else:
                        nastr = ""
                        nnf = n['r_a']
                        if n['t'] == "Function":
                            for nf in nnf:
                                # print nf
                                if nf.has_key('a') and nf.has_key('t'):
                                    nastr = "%s,%s: %s"%(nastr ,nf['a'],nf['t'])
                            nastr = "(res:{%s})=>void"%nastr[1:len(nastr)]
                        elif n['t'] == "Object":
                            for nf1 in nnf:
                                if nf1.has_key('a') and nf1.has_key('t'):
                                    nastr = "%s,%s?: %s"%(nastr ,nf1['a'],nf1['t'])

                            nastr = "{%s}"%nastr[1:len(nastr)]

                        nstr = "%s,%s:%s"%(nstr,n['n'],nastr)
    
                if len(nstr) > 0:
                    nstr = nstr[1:len(nstr)]
            writeContent.append('\t/**\n\t* %s \n\t*/\n\t%s;\n' % (mm[1], wtMethod(mm[0],nstr)))
        writeContent.append('}\n');

    writeStrs = "".join(writeContent)

    # 以下是爬取过程需要替换的一些字符，否则d.ts会有一些错误
    writeStrs = writeStrs.replace("Array.","Array")
    writeStrs = writeStrs.replace(": object",": Object")
    writeStrs = writeStrs.replace(": function",": Function")
    writeStrs = writeStrs.replace(": arraykvdata",": Array<KVData>")
    writeStrs = writeStrs.replace(": Promise",": Promise<any>")
    writeStrs = writeStrs.replace(" Image"," WxImage")
    writeStrs = writeStrs.replace(" Touch"," WxTouch")
    writeStrs = writeStrs.replace("<Touch","<WxTouch")
    writeStrs = writeStrs.replace(" RenderingContext"," WxRenderingContext")
    # writeStrs = writeStrs.replace(": Image",": WxImage{")
    with open('wx.d.ts', 'w') as fp:  
        # 开始写文件
        fp.write(writeStrs);

# 读取文件
def readaHtml1():
    from wxProcess import processWx,readClsFile
    f =None
    with open('page/first.html', 'r') as fp:
        f = fp.read();
    bsObj=BeautifulSoup(f,"html.parser")
    apis = [];
    acls = {
        'c':{},
        'm':[],
        'a':[],
        # 't'
    }
    printtms = 0;
    bdys = bsObj.find_all("section");
    for tby in bdys[0].find_all("tbody"):
        for tr in tby.find_all("tr"):
            td = tr.find_all("td")
            printtms = printtms + 1;
            # print "analys{0}".format('.'*(printtms%3 + 1))
            print "analys %s"%td[0].text.strip()
            n,clsss,method = processWx(td[0].text.strip())
            [argt,arg,rtval] = readClsFile(clsss,method)

            method = [method,rtval]
            if clsss==None:
                if argt == ONLY_METHOD and arg != None:
                    acls['m'].append([method,td[1].text.strip(),arg]);
                elif NOT_METHOD_CLS == argt:
                    continue
                else:
                    acls['m'].append([method,td[1].text.strip()])

            elif method[0]==None:
                if argt ==CLS_ATTR and arg != None:
                    if not acls['c'].has_key(clsss):
                        acls['c'][clsss] = {
                            'a': arg,
                            'm': [],
                            'i':td[1].text.strip()
                        }
                    else:
                        acls['c'][clsss]['i'] = td[1].text.strip()
                        acls['c'][clsss]['a'] = arg
                else:
                    if not acls['c'].has_key(clsss):
                        acls['c'][clsss] = {
                            'a': [],
                            'm': [],
                            'i':td[1].text.strip()
                        }
                    else:
                        acls['c'][clsss]['i'] = td[1].text.strip()
            elif not acls['c'].has_key(clsss):
                acls['c'][clsss] = {
                    'a':[],
                    'm':[],
                    'i':''
                }
                if CLS_METHOD == argt and len(arg)> 0:
                    acls['c'][clsss]['m'].append([method,td[1].text.strip(),arg])
                else:
                    acls['c'][clsss]['m'].append([method,td[1].text.strip()])
            else:
                if CLS_METHOD == argt and len(arg)> 0:
                    acls['c'][clsss]['m'].append([method,td[1].text.strip(),arg])
                else:
                    acls['c'][clsss]['m'].append([method,td[1].text.strip()])

            # apis.append({"cls":td[0],"intro":td[1]})

    bdys = bsObj.find_all("nav");

    for bd in bdys:
        if bd['role'] == "navigation":
            uls = bd.find_all("ul")
            for ul in uls:
                lis = ul.find_all("li")
                # print lis
                for b in lis:
                    # print b['class']
                    if b['class'] == [u"chapter"] and firstCrisansi(b['data-name']):
                        clsss = b['data-name']
                        if not clsss[0:1].islower() and clsss.find(".") == -1:
                            [argt,arg,rtval] = readClsFile(b['data-name'],None)
                            method = [None,rtval]
                            if argt ==CLS_ATTR and arg != None:
                                narg = False
                                keys = {}
                                for i in range(0,len(arg)):
                                    if arg[i]['a'].find(".") > -1:
                                        # print "hello%s ---"%arg[i]['a']
                                        sarg = arg[i]['a'].split(".")
                                        arg[i]['a'] = sarg[1]
                                        if not keys.has_key(sarg[0]):
                                            keys[sarg[0]] = [arg[i]]
                                        else:
                                            keys[sarg[0]].append(arg[i])
                                        narg = True
                                
                                if not narg:
                                    keys = arg
                                
                                
                                if not acls['c'].has_key(clsss):
                                    acls['c'][clsss] = {
                                        'a': keys,
                                        'm': [],
                                        'i':""#td[1].text.strip()
                                    }
                                else:
                                    if keys != {}:
                                        acls['c'][clsss]['a'] = keys
                            else:
                                if not acls['c'].has_key(clsss):
                                    acls['c'][clsss] = {
                                        'a': [],
                                        'm': [],
                                        'i':""#td[1].text.strip()
                                    }
                                # else:
                               #     acls['c'][clsss]['i'] = td[1].text.strip()

    return acls;

def getRidofDouble(arr):
    m = {}
    for i in arr:
        if not m.has_key(i):
            m[i] = True
    return  m.keys()



# 这里主要是爬取一些类的接口，比如 Kvdata之类的，为了书写
def getApiHtmls():
    f =None
    with open('page/first.html', 'r') as fp:
        f = fp.read();
    bsObj=BeautifulSoup(f,"html.parser")

    urls = []

    existfiles = []
    # 这里找到没有下载的文件进行下载
    noexists = []

    bdys = bsObj.find_all("section");
    # find right apis
    for tby in bdys[0].find_all("tbody"):
        for tr in tby.find_all("tr"):
            td = tr.find_all("td")
            urls.append(td[0].find('a')['href'])

    for url in urls:
        x = url.split('/')
        x = x[len(x)-1];
        if not os.path.isfile("page/%s"%x) or FORCE_RELOAD_HTML:
            noexists.append([x[0:-5], url])
        else:
            existfiles.append(x[0:-5])

    # find left nav apis
    bdys = bsObj.find_all("nav");
    for bd in bdys:
        if bd['role'] == "navigation":
            uls = bd.find_all("ul")
            for ul in uls:
                lis = ul.find_all("li")
                for b in lis:
                    # 
                    
                    if b['class'] == [u"chapter"] and firstCrisansi(b['data-name']):
                        tmp1 = b['data-name']
                        c = b['data-path']
                        #具体的类或者方法名
                        tmp = c[2:len(c)].split("/")
                        tmp = tmp[len(tmp)-1]

                        # 这里主要针对一个类做一个区分，由于书写习惯，类都是以大写字母开头的
                        if not tmp[0:1].islower() and tmp1.find(".") == -1:
                            # 需要判断一下文件是否存在的
                            if not os.path.isfile("page/%s"%tmp) or FORCE_RELOAD_HTML :
                                noexists.append([b['data-name'],c[2:len(c)]])
                            else:
                                existfiles.append(tmp1);
    existfiles = getRidofDouble(existfiles)
    print "%d files are exists as follow\n--------begin %s \n--------end\nnow start craw"%( len(existfiles),"\n".join(existfiles))

    if len(noexists) > 0:
        noexists.sort(lambda x,y:ord(x[0][0]) - ord(y[0][0]))
        #开始爬虫111111，这里只做了简单的一层爬取
        import time
        import random
        session = requests.session();
        writednum = 0;
        for a in noexists:
            # as a normal man to read api
            time.sleep(1+random.random());
            writednum = writednum+1;
            print "start get file %s at %d"%(a[1] ,writednum)
            get_evy_url(session,a[1]);


# 判断一个unicode是否是汉字，true 不是汉字
def firstCrisansi(text):
    if len(text) ==0:
        return ;
    uchar =  text[0:1]
    """判断一个unicode是否是汉字  uchar >= u'u4e00' and uchar<=u'u9fa5' """
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return False
    else:
        return True


def returnPromiseApiStr():
    return '\n/**\n*\n*/\nPromise{\n\t/**传递*/\n\tthen(callback:(res)=>void):Promise;\n\t/**异常*/\n\tcatch(callback:(res)=>void):Promise;\n};\n'

def printddd():
    pass


if __name__ == '__main__':

    # change this to refresh wx api,and have a coffee to wait for res
    FORCE_RELOAD_HTML = False
    if FORCE_RELOAD_HTML:
        print "force to reload mode"

    print "1---------------------------------start get html page"
    if not os.path.exists('page/first.html'):
        s,cont = create_session()
        getApiHtmls()
    else:
        getApiHtmls()

    print "2---------------------------------start analys file"
    acls = readaHtml1()
    print "3---------------------------------start write file"
    writeFile2(acls)
    print '''Success!!!!
            take the wx.d.ts  to your project'''
