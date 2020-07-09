# 下载 web of science 已有的并且可直接获取的pdf文档，并将可下载的pdf链接标记为『111111111111』以求明显

import requests
import pandas as pd

##基于已有的csv表格里面的pdf_link下载pdf
# （不是所有有pdf链接的都可以下载，有些是文件链接可下载，有些是网站链接需手工下载）
paperCsv_path = "article_information/paperInfo.csv"
article_info = pd.read_csv(paperCsv_path, index_col=0)
save_path = "article_pdf/" #存储pdf的路径

index = article_info.index.values
for i in index:
    if(article_info.loc[i, "pdf_link"] != None):
        requests_pdf_url = article_info.loc[i, "pdf_link"]
        try:
            r = requests.get(requests_pdf_url)

            filename =  save_path + article_info.loc[i, "title"]+".pdf"
            article_info.loc[i, "Download_SuccessOrDefeat"] = "Success"
            with open(filename, 'wb+') as f:
                f.write(r.content)
        except:
            article_info.loc[i,  "Download_SuccessOrDefeat"] = "Defeat"
            continue
