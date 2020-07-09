import Spider_by_VZ.Main_Methods as pagesToDic
import warnings
warnings.filterwarnings("ignore")

import pickle
import pandas as pd
import numpy as np
def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def Merge(dict1, dict2):
    dict2.update(dict1)
    return dict2

def toString(list1, key):
    this_string = ""
    if key == 'simply_author_name' or key == 'whole__author_name':
        for i in range(len(list1)):
            this_string += list1[i].replace(',', '')+","
    else:
        for i in range(len(list1)):
            this_string += list1[i]+","

    return this_string[:-1]

if __name__ == "__main__":
    #这是文献所在的url，里面包含验证信息。
    # 先将web of science 检索结果进行翻页一下，以获得最后的page=字符串，
    # 并将此时的连接截取除了最后的数字外，赋值给url——root

    url_root = "http://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=GeneralSearch&parentQid=&qid=1&SID=8E1WyxAPwFrQXRlfZw1&&update_back2search_link_param=yes&page="
    nums_page = 1
    #指定文献信息表格存的路径以及名字
    filename = "article_information/paperInfo.csv"

    #获取文献信息  用字典存储，字典文件备份在Mid_Process_File文件里
    paper_Dic_Info = pagesToDic.Start_Scarp(root=url_root, nums_page=nums_page, filename=None)

    info_dict = paper_Dic_Info

    columns = ['title','Volume','Issue','Pages','whole__author_name','simply_author_name',	'reprint author','DOI','reprint address','Abstract','Keywords','Document Type','Publisher','Research Domain','Published Date','impact_factor','Keywords_plus','joural','pdf_link',"Download_SuccessOrDefeat"]


    article_nums = len(info_dict)


    df = pd.DataFrame(index=range(1, article_nums), columns=columns)

    for index in info_dict.keys():
        for column in info_dict[index].keys():
            if (type(info_dict[index][column]) == type([])):
                df.loc[index, column] = toString(info_dict[index][column], column)
            else:
                if column == 'reprint author':
                    df.loc[index, column] = info_dict[index][column].replace(',', '')
                else:
                    df.loc[index, column] = info_dict[index][column]

    df.to_csv(filename)


