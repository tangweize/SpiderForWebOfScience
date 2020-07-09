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



def keyWordsplus_extract(abstract_list):
    keywords_dic = dict()
    print("进来啊啊！！！！！")
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

    # abstract_dic = dict()
    # abstract_dic['Abstract'] = abstract_text
    # return abstract_dic



def Merge(dict1, dict2):
    dict2.update(dict1)
    return dict2




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

def extract_info(article_url):
    author_name = {}
    all_info = {}
    this_html = getHTMLText(article_url)

    re_title = r'<input type="hidden" name="00N70000002BdnX"[\s\S]*?/>'

    title_html = re.findall(re_title, this_html)

    soup = BeautifulSoup(title_html[0], 'html.parser')

    # title 标题提取完成。
    title = soup.input['value']
    basic_info = dict()
    basic_info['title'] = title


    #keywords_plus 匹配
    re_Keywords_plus=r'<p class="FR_field">\n<span class="FR_label">KeyWords Plus[\s\S]*?</p>'
    keywords_plus_list = re.findall(re_Keywords_plus, this_html)
    keywords_plus_info = keyWordsplus_extract(keywords_plus_list)

    #期刊 及影响因子
    re_journal_plus = r'<source_title_txt_label lang_id="en-us">[\s\S]*?</source_title_txt_label>'
    joural_list = re.findall(re_journal_plus, this_html)
    joural_info = joural_extract(joural_list)


    re_impact_factor = r'<span class="FR_label">  Impact Factor </span>[\s\S]*?</tr>'
    impact_factor_list = re.findall(re_impact_factor, this_html)

    impact_factor_info = impact_factor_extract(impact_factor_list)


    all_info = Merge(all_info, basic_info)
    all_info = Merge(all_info, keywords_plus_info)

    all_info = Merge(all_info, joural_info)
    all_info = Merge(all_info, impact_factor_info)
    # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(all_info)

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
        re_text = r'<span class="smallV110">.*?value>'
        re_text1 = r'<span class="smallV110">[\s\S]*?value>'
        match_list = re.findall(re_text1, s.text)  #获得所有文献的连接和标题。
        page_article_url = []
        for href_string in match_list:
            soup = BeautifulSoup(href_string, 'html.parser')
            prefix = "http://apps.webofknowledge.com/"
            page_article_url.append(prefix+soup.a['href'])

        #.......asdsdaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        #page_article_url[0] = "http://apps.webofknowledge.com//full_record.do?product=WOS&search_mode=GeneralSearch&qid=2&SID=8CtM5jzZ1tzj4s4FXBu&page=12&doc=115"

        for article_url in page_article_url:
            print("======分割线")
            print(article_url)
            INFO[count] = extract_info(article_url)
            print("完成了：  ", count / 153)
            count += 1


    save_obj(INFO, "2018_article_addinfo")


