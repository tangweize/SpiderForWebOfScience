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
info_dict = load_obj("2018_article_addinfo")

columns = list(info_dict[1].keys())

#columns = ['title','Volume','Issue','Pages','whole__author_name','simply_author_name',	'reprint author','DOI','reprint address','Abstract','Keywords','Document Type','Publisher','Research Domain','Published Date','pdf_link']


#
# print(columns)
# print(info_dict[1]['simply_author_name'])
article_nums = len(info_dict)
# for i in range(1,5):
#     print(list(info_dict[i].keys()))

df = pd.DataFrame(index=range(1,article_nums), columns=columns)

for index in info_dict.keys():
    for column in info_dict[index].keys():
        if(type(info_dict[index][column]) == type([])):
            df.loc[index, column] = toString(info_dict[index][column], column)
        else:
            if column == 'reprint author':
                df.loc[index, column] = info_dict[index][column].replace(',','')
            else:
                df.loc[index, column] = info_dict[index][column]


df.to_csv("2018高温合金文献_add.csv")