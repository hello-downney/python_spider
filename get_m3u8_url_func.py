
import requests
import re
from bs4 import BeautifulSoup
obj1 = re.compile(r"var temPlayRenderCode = .*?src='(?P<m3u8_url>.*?)' title='(?P<chapter_name>.*?)' frameborder=0 allowf", re.S)
headers = {
    "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36 Edg/143.0.0.0",
    "referer": "https://dxfbk.com/"
}
def get_all_url(url):
    response = requests.get(url=url,headers=headers)
    page = BeautifulSoup(response.text,"lxml")
    soup = page.find_all("ul",class_="anthology-list-play size playEpisodes",style="display: block;")[1]
    url_lst = soup.find_all("a")
    all_url = []
    for i in url_lst:
        url = i.get("href")
        url = "https://www.yhmc.cc"+url
        all_url.append(url)
    # all_url = all_url[9:10]
    print(all_url)
    return all_url


def get_m3u8_url(anime_url,location):
    import os
    l = fr"{location}"
    all_url = get_all_url(anime_url)
    m3u8_url_lst = []
    for i in all_url:
        response = requests.get(url=i,headers=headers)
        aaa = obj1.search(response.text)
        url = aaa.group("m3u8_url").split("?url=")[1]
        chapter_name = aaa.group("chapter_name")
        t = (chapter_name, url)
        m3u8_url_lst.append(t)
    subdirs = [name for name in os.listdir(l)
               if os.path.isdir(os.path.join(l, name))]
    for subdir in subdirs:
        num = 0
        for k in m3u8_url_lst:
            if subdir in k:
                m3u8_url_lst.remove(m3u8_url_lst[num])
                break
            num += 1


    print(m3u8_url_lst)
    return m3u8_url_lst
if __name__ == '__main__':
    get_all_url("https://www.yhmf.cc/v/1311323/272")
