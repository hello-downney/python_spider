"""
主要爬樱花动漫的加速云！！！！！！！！！！！！！！！！！不是加速云要改get_m3u8_url_func函数的beautifulsoup列表切片[]
樱花动漫网址https://www.yhmc.cc/index.html
1.写好get_m3u8_url_func的函数，返回的是列表，每个元素是元组（chapter_name,m3u8_url）m3u8_url是要可以直接请求得到ts的那种
2.写好download_chapter_func的函数，然后在这个函数的前面导入import函数get_m3u8_url_func
3.然后在另外的文件导入download_chapter_func函数

！！！！！！！！请修改文件夹路径！！！！！！！！请修改文件夹路径！！！！！！！！请修改文件夹路径！！！！！！！！请修改文件夹路径！！！！！！！！！！！！！！！！
"""
from download_chapter_func import *
from get_m3u8_url_func import *
if __name__ == '__main__':
    anime_url = input("已经加了自动检测已下载视频功能，检测存在的文件夹\n（所以如果某一集没下载完就只需要把那一集的文件夹及其文件删除）\n输入要爬的动漫url：")
    loca = input("输入装资源的文件夹名（如C:\未闻花名）：")#提前在对应位置建立对应文件夹！！！！！！！！！！！！！！！！！！！！！！！
    asyncio.run(main(anime_url, loca))










