# -*- coding: utf-8 -*-
import sys
import os
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')

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

#process attribute
def processAttr(content):
    rtval = None
    h5s = content.find_all("h5")
    ps = content.find_all("p")
    nps = []
    # print len(ps)
    for i in range(0,len(ps)):
        if not ps[i].find_all("strong"):
            nps.append(ps[i]);
            # print ps[i]
    ps = nps;
    # print len(ps)


    if not h5s:
        return None
    a = []#{a,i}
    lenh5 = len(h5s)
    lenp = len(ps)
    for i in range(0,lenh5):
        h5 = h5s[i].text.lstrip();
        h5 = h5.rstrip();


        if h5.find('(') > 0 :
            continue
        sp = h5s[i].text.split(" ")
        
        if sp[0] == "function":
            sp[0] = "Function"

        if len(sp) == 2:
            a.append({
                'a':sp[1],
                'r':sp[0],
                'i':ps[i+1].text
                })
        elif len(sp) == 1:
            a.append({
                'a':sp[0][0:1],
                'r':sp[0],
                'i':ps[1+ i].text
                })
    return a,rtval

def processArgs(content):
    a = []
    rtval = 'void'
    h5s = content.find_all("h5")
    ps = content.find_all("p")
    h3 = content.find('h3')

    h3str = h3.text;
    h3arr = h3str.split("(");
    if len(h3arr) == 2:
        rtarr = h3arr[0].split(" ")
        if len(rtarr) == 2:
            rtval = rtarr[0]

        args2 = h3arr[1][0:len(h3arr[1])-1].split(",")
        if len(args2) > 0:
            for x in args2:
                x = x.lstrip()
                x = x.rstrip()
                if x== '':
                    # print "%-50s %s"%(h3['id'],h3.text)
                    continue
                

                xx  = x.split(" ")
                # print xx
                a.append({
                    'n':xx[1],
                    't':xx[0],
                    'r_a':[],
                    'rt':None
                })
    return a,rtval



# def processWxAttr(content):
#     pass

##获取头部对应列表
ATTR_NAMES = {u"属性":'a',u"类型":'t',u"说明":'i',u'默认值':'d',u'是否必填':'mw'}
def getHeaderNameIdx(arrs):
    res = {}
    for i in range(0,len(arrs)):
        attext = arrs[i].text
        if ATTR_NAMES.has_key(attext):
            res[ATTR_NAMES[attext]] = i
    return res

# 处理 method 的callback 参数
def processMethodCallbackarg(content):
    arg = {
        'n':'callback',#参数名
        't':'Function',#参数类型
        'r_a':[],#参数为函数的参数列表或者对象的属性列表
        'rt':None #返回类型
    }
    h6s = content.find_all("h6")
    if len(h6s) > 0 and h6s[0].text == "参数":
        fnargs = []
        tbs = content.find_all("table")
        for tb in tbs:
            # 解析头部
            ths =tb.find("thead").find_all("th")
            hidxs = getHeaderNameIdx(ths)

            tby =  tb.find("tbody")
            trs = tby.find_all("tr")
            
            
            for tr in trs:
                tds =  tr.find_all("td")
                # fnargs['a'] = tds[hidxs['a']].text
                # fnargs['t'] = tds[hidxs['t']].text
                # fnargs['i'] = tds[hidxs['i']].text
                tmp = {}
                for i in hidxs:
                    tmp[i] = tds[hidxs[i]].text
                    tmp[i] = tmp[i].replace("/","|")
                fnargs.append(tmp)
        arg['r_a'] = fnargs
    return arg

# 处理method 的 object 参数
# 这里暂时不处理object里面的返回值什么的
# 稍微弱一点的object
def processMethodObjectarg(content):
    arg = {
        'n':'obj',#参数名
        't':'Object',#参数类型
        'r_a':[],#参数为函数的参数列表或者对象的属性列表,无则为空
        'rt':None #返回类型
    }

    fnargs = []
    tbs = content.find_all("table")
    for tb in tbs:
        # 解析头部
        ths =tb.find("thead").find_all("th")
        hidxs = getHeaderNameIdx(ths)

        tby =  tb.find("tbody")
        trs = tby.find_all("tr")
        for tr in trs:
            tds =  tr.find_all("td")

            tmp ={}
            for i in hidxs:
                tmp[i] = tds[hidxs[i]].text
                tmp[i] = tmp[i].replace("/","|")
            fnargs.append(tmp)
        arg['r_a'] = fnargs
        return arg

def processWithRtVal(content):
    pass

def processClsMd(content):
    a = []

    h3 = content.find("h3")
    h3id = h3['id'].split("-")

    argt = None
    # return val
    rtval = None

    if len(h3id) > 1:
        argt = h3id[1]
    if argt == None:
        pass
    # 处理method
    elif argt == "callback":
        arg = processMethodCallbackarg(content)
        a.append(arg)

    elif argt == "object":
        arg = processMethodObjectarg(content)
        a.append(arg)
    else:
        h3str = h3.text;
        h3arr = h3str.split("(");
        # return val
        # rtval = None
        # arg = {
        #     'n':'obj',#参数名
        #     't':'Object',#参数类型
        #     'r_a':[],#参数为函数的参数列表或者对象的属性列表,无则为空
        #     'rt':None #返回类型
        # }
        if len(h3arr) == 2:
            rtarr = h3arr[0].split(" ")
            if len(rtarr) == 2:
                rtval = rtarr[0]

            args2 = h3arr[1][0:len(h3arr[1])-1].split(",")
            if len(args2) > 0:
                for x in args2:
                    x = x.lstrip()
                    x = x.rstrip()
                    if x== '':
                        # print "%-50s %s"%(h3['id'],h3.text)
                        continue
                    xx  = x.split(" ")
                    a.append({
                        'n':xx[1],
                        't':xx[0],
                        'r_a':[],
                        'rt':None
                    })
            else:
                pass
                # print "%-50s %s"%(h3['id'],h3.text)
        else:
            pass
            # print "%-50s %s"%(h3['id'],h3.text)
    return a,rtval

# content is a bs Object
def dowithStr(t,content,c,m):
    if t == 1:
        h4 = content.find_all("h4")
        if len(h4)==0:
            return ONLY_CLS,None,None
        if h4[0].text.strip() == u"属性":
            a1,a2 = processAttr(content)
            return CLS_ATTR,a1,a2
        else:
            return None,None,None

    elif t == 0:
        h4 = content.find_all("h4")
        if len(h4)==0:
            return ONLY_METHOD,None,None

        if h4[0].text.strip() == u"参数":
            pre = content.find_all("pre")
            if len(pre) > 0:
                return NOT_METHOD_CLS,None,None
            a1,a2 = processArgs(content)
            return ONLY_METHOD,a1,a2
        else:
            return None,None,None
    elif t == 2:
        # if c == 'wx':
        #     return CLS_METHOD,processWxAttr(content)
        # else:
        a1,a2 = processClsMd(content)
        return  CLS_METHOD,a1,a2
    else:
        return -1,None,None


# rtval
# 0 only method
# 1 wx method
# 2 class
# 3 class method

def processWx(text):
    if text.startswith('wx'):
        return 1,"wx",text[3:len(text)]
    isMethod = text[0:1].islower()
    posd = text.find(".")
    if posd == -1:
        if isMethod:
            return 0,None,text
        else:
            return 2,text,None
    else:
        return 3,text[0:posd],text[posd+1:len(text)]      

# 这里用读取文件的形式，事先爬虫下来的文件
def readClsFile(clas,method):
    path = ""
    t = 0;
    if clas == None:
        path = "page/%s.html"%method
    elif method == None:
        path = "page/%s.html"%clas
        t = 1
    else:
        path = "page/%s.%s.html"%(clas,method)
        t = 2

    if os.path.isfile(path):
        f = open(path,"r")
        bsObj=BeautifulSoup(f.read(),"html.parser")
        f.close();
        a1,a2,a3 = dowithStr(t,bsObj.find("section"),clas,method)
        return [a1,a2,a3]
    else:
        print "---------------not exist file: %s"%path
        return [None,None,None]



