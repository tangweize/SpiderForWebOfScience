import re
import os
from multiprocessing import Process
from multiprocessing import Manager
import requests
import time
import xlrd
from bs4 import BeautifulSoup
from lxml import etree
import pickle
def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)



class SpiderMain(object):
    def __init__(self, sid, kanming):
        self.hearders = {
            'Origin': 'https://apps.webofknowledge.com',
            'Referer': 'https://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=R1ZsJrXOFAcTqsL6uqh&preferencesSaved=',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.form_data = {
            'fieldCount': 1,
            'action': 'search',
            'product': 'WOS',
            'search_mode': 'GeneralSearch',
            'SID': sid,
            'max_field_count': 25,
            'formUpdated': 'true',
            'value(input1)': kanming,
            'value(select1)': 'TI',
            'value(hidInput1)': '',
            'limitStatus': 'collapsed',
            'ss_lemmatization': 'On',
            'ss_spellchecking': 'Suggest',
            'SinceLastVisit_UTC': '',
            'SinceLastVisit_DATE': '',
            'period': 'Range Selection',
            'range': 'ALL',
            'startYear': '1982',
            'endYear': '2017',
            'update_back2search_link_param': 'yes',
            'ssStatus': 'display:none',
            'ss_showsuggestions': 'ON',
            'ss_query_language': 'auto',
            'ss_numDefaultGeneralSearchFields': 1,
            'rs_sort_by': 'PY.D;LD.D;SO.A;VL.D;PG.A;AU.A'
        }
        self.form_data2 = {
            'product': 'WOS',
            'prev_search_mode': 'CombineSearches',
            'search_mode': 'CombineSearches',
            'SID': sid,
            'action': 'remove',
            'goToPageLoc': 'SearchHistoryTableBanner',
            'currUrl': 'https://apps.webofknowledge.com/WOS_CombineSearches_input.do?SID=' + sid + '&product=WOS&search_mode=CombineSearches',
            'x': 48,
            'y': 9,
            'dSet': 1
        }

    def craw(self, root_url, i):
        try:
            s = requests.Session()
            r = s.post(root_url, data=self.form_data, headers=self.hearders)
            r.encoding = r.apparent_encoding
            tree = etree.HTML(r.text)
            cited = tree.xpath("//div[@class='search-results-data-cite']/a/text()")
            download = tree.xpath(".//div[@class='alum_text']/span/text()")
            flag = 0
            print(cited, download, r.url)
            flag = 0
            return cited, download, flag
        except Exception as e:
            # 出现错误，再次try，以提高结果成功率
            if i == 0:
                print(e)
                print(i)
                flag = 1
                return cited, download, flag

    def delete_history(self):
        murl = 'https://apps.webofknowledge.com/WOS_CombineSearches.do'
        s = requests.Session()
        s.post(murl, data=self.form_data2, headers=self.hearders)


class MyThread(Process):
    def __init__(self, sid, kanming, i, dic):
        Process.__init__(self)
        self.row = i
        self.sid = sid
        self.kanming = kanming
        self.dic = dic

    def run(self):
        self.cited, self.download, self.fl = SpiderMain(self.sid, self.kanming).craw(root_url, self.row)
        self.dic[str(self.row)] = Result(self.download, self.cited, self.fl, self.kanming, self.row)


class Result():
    def __init__(self, download, cited, fl, kanming, row):
        super().__init__()
        self.row = row
        self.kanming = kanming
        self.fl = fl
        self.cited = cited
        self.download = download



def runn(sid, kanming, i, d):
    ar, ref, fl = SpiderMain(sid, kanming).craw(root_url, row)
    d[str(i)] = Result(ar, ref, fl, kanming, i)
    print(d)

def getHTMLText(url):
    try:
        kv = {"user-agent":"Mozilla/5.0"}
        r = requests.get(url, headers=kv)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "产生异常"

def download(url):

    path = url.split("/")[-1]
    try:
        if not os.path.exists(path):
            r = requests.get(url)
            with open(path, 'wb') as f:
                f.write(r.content)
                f.close()
                print("文件保存成功")
        else:
            print("文件已存在")
    except:
        print("爬去失败")

def match_target(re_text, text):
    match_list = re.findall(re_text, text)
    print(match_list)

def getAuthor_Name(Many_INFO_html):


    html = Many_INFO_html[0]
    Author_soup = BeautifulSoup(html, 'html.parser')

    author_name = []
    for i in Author_soup.p.contents:
        try:
            if i.name == 'a':
                author_name.append(i.next)
                author_name.append(i.nextSibling)
        except:
            continue
        # print(
        #     "========================================================================================================================")
    Whole_name = [author_name[i] for i in range(len(author_name)) if i % 2 == 0]
    Simply_name = [author_name[i][2:-1] for i in range(len(author_name)) if i % 2 == 1]

    return Simply_name,Whole_name


def juan_ye_DOI_Year_Type(Many_INFO_html):  #获取卷，页码，DOI,年份，类型

    #提取一下内容
    Columns = ['Volume','Pages','DOI','Published:','Document Type','Publisher','Research Domain','Issue']
    basic_INFO = dict()


    boarder = len(Many_INFO_html)
    for i in range(1,min(10, boarder)):
        html = Many_INFO_html[i]
        Author_soup = BeautifulSoup(html, 'html.parser')

        temp_info = []
        for i in Author_soup.p.contents:
            temp_info.append(i.string)

        new_info = [i for i in temp_info if i!='\n' and i!=None ]
        basic_INFO[new_info[0][:-1]] = new_info[1:]



    keys = basic_INFO.keys()
    daishanchu = []
    for key in keys:
        if key not in Columns:
            daishanchu.append(key)
    if 'Published:' in keys:
        basic_INFO["Published Date"] = basic_INFO['Published:']
        daishanchu.append('Published:')

    for i in daishanchu:
        del basic_INFO[i]


    return basic_INFO


def abstract(abstract_list):
    html = abstract_list[0]
    abstract_soup = BeautifulSoup(html, 'html.parser')
    abstract_text = ""
    list1 = []
    for i in abstract_soup.p.contents:

        if i != '\n' and i != None and i != "":
            if type(i.string) != type(None):
                abstract_text += i.string

            #abstract_text+= i.string
    abstract_dic = dict()
    abstract_dic['Abstract'] = abstract_text
    return abstract_dic

def keyWords_extract(abstract_list):
    keywords_dic = dict()
    try:
        html = abstract_list[0]
        abstract_soup = BeautifulSoup(html, 'html.parser')
        keywords_list = []
        for i in abstract_soup.p.contents:
            if i.string != '\n' and i.string != None and i.string != "" and i.string != "; ":
                keywords_list.append(i.string)
        keywords_dic['Keywords'] = keywords_list[1:]
    except:
        keywords_dic['Keywords'] = [""]



    print(keywords_dic)
    return keywords_dic

    # abstract_dic = dict()
    # abstract_dic['Abstract'] = abstract_text
    # return abstract_dic


def keyWordsplus_extract(abstract_list):
    keywords_dic = dict()

    soup1 = BeautifulSoup('<b class="boldest">Extremely bold</b>')
    tag = soup1.b

    try:
        html = abstract_list[0]
        abstract_soup = BeautifulSoup(html, 'html.parser')
        keywords_list = []
        for i in abstract_soup.contents[0].contents:
            if type(i) == type(tag):
                if "href" in i.attrs:
                    string_temp = i["href"]
                    re_title = r'value=.*?&'
                    text = re.findall(re_title, string_temp)
                    keywords_list += text[0][6:-1].split("+")



        keywords_dic['Keywords_plus'] = keywords_list
    except:
        keywords_dic['Keywords_plus'] = [""]
    return keywords_dic

def joural_extract(joural_list):


    bas = dict()
    try:
        html = joural_list[0]
        abstract_soup = BeautifulSoup(html, 'html.parser')
        joural_list = abstract_soup.value.string
        bas['joural'] = joural_list

    except:
        bas['joural'] = ""
    return bas

def impact_factor_extract(joural_list):
    bas = dict()

    try:
        html = joural_list[0]
        abstract_soup = BeautifulSoup(html, 'html.parser')
        tag_soup = abstract_soup.tr
        joural_list = tag_soup.contents[3].string
        bas['impact_factor'] = joural_list

    except:
        bas['impact_factor'] = ""
    return bas


def pdf_extract(pdf_htmlList):
    html = pdf_htmlList[0]
    abstract_soup = BeautifulSoup(html, 'html.parser')

    try:
        value = abstract_soup.input.nextSibling["value"]
    except:
        value = ""

    return value



def Merge(dict1, dict2):
    dict2.update(dict1)
    return dict2


def reprint_extract(reprint_htmlList):
    html = reprint_htmlList[0]
    abstract_soup = BeautifulSoup(html, 'html.parser')

    Corresponding_Info = []
    for i in abstract_soup.p.contents:
        if i.string != '\n' and i.string != None and i.string != "" and i.string != "; ":
            Corresponding_Info.append(i.string)


    # print(Corresponding_Info)
    reprint_info = dict()
    reprint_info['reprint author'] = Corresponding_Info[1][:-len(" (reprint author) ")]

    Corresponding_address = []
    a = abstract_soup.td.next_sibling

    reprint_info["reprint address"] = a.contents[0]


    return reprint_info


def extract_info(article_url):
    author_name = {}
    all_info = {}
    this_html = getHTMLText(article_url)

    re_title = r'<input type="hidden" name="00N70000002BdnX"[\s\S]*?/>'

    title_html = re.findall(re_title, this_html)

    soup = BeautifulSoup(title_html[0], 'html.parser')

    # title 标题提取完成。
    title = soup.input['value']


    #提取所有结构化数据，找到所在网页范围
    re_many_Info = r'<p class="FR_field">[\s\S]*?</p>'
    Many_INFO_html = re.findall(re_many_Info, this_html)
    author_name['whole__author_name'], author_name['simply_author_name'] = getAuthor_Name(Many_INFO_html)

    #卷，页码，DOI。。。
    basic_info = juan_ye_DOI_Year_Type(Many_INFO_html)
    basic_info['title'] = title

    #摘要
    re_Abstract = r'<div class="title3">Abstract</div>[\s\S]*?</p>'
    abstract_list = re.findall(re_Abstract, this_html)
    abstract_info = abstract(abstract_list)
    print("------------------------------------------------------------------")

    #关键字
    re_Keywords = r'<div class="title3">Keywords</div>[\s\S]*?</p>'
    keywords_list = re.findall(re_Keywords, this_html)
    keywords_info = keyWords_extract(keywords_list)


    #通讯作者及地址
    re_reprint = r'<div class="title3">Author Information</div>[\s\S]*?</p>'
    reprint_htmlList = re.findall(re_reprint, this_html)
    reprint_Info = reprint_extract(reprint_htmlList)

    #pdfl链接
    re_pdf = r'<td class="FRleftColumn" >[\s\S]*?</div>'
    pdf_htmlList = re.findall(re_pdf, this_html)
    basic_info['pdf_link'] = pdf_extract(pdf_htmlList)


    all_info = Merge(all_info, basic_info)
    all_info = Merge(all_info, abstract_info)
    all_info = Merge(all_info,keywords_info)
    all_info = Merge(all_info, reprint_Info)
    all_info = Merge(all_info, author_name)


    return all_info

article_info = dict()
if __name__ == "__main__":

    #指定的页数 目前1-xx页
    page_nums = list(range(1,20))

    root = "http://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=GeneralSearch&parentQid=&qid=1&SID=8E1WyxAPwFrQXRlfZw1&&update_back2search_link_param=yes&page="
    count = 1
    INFO = {}
    for i in page_nums:
        temp_root = root + str(i)
        s = requests.get(temp_root)
        print(s)
        re_text = r'<span class="smallV110">.*?value>'
        re_text1 = r'<span class="smallV110">[\s\S]*?value>'
        match_list = re.findall(re_text1, s.text)  #获得所有文献的连接和标题。
        page_article_url = []
        for href_string in match_list:
            soup = BeautifulSoup(href_string, 'html.parser')
            prefix = "http://apps.webofknowledge.com/"
            page_article_url.append(prefix+soup.a['href'])


        for article_url in page_article_url:
            print("======分割线")
            print(article_url)
            INFO[count] = extract_info(article_url)
            print(INFO)
            print("完成了：  ", count / 153)
            count += 1


    save_obj(INFO, "Mid_Process_File/2018_article")


