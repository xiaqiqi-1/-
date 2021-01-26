import urllib.request
import urllib.error
from io import StringIO
import os
import re
import time
import socket
from fake_useragent import UserAgent
from requests import *
from bs4 import BeautifulSoup
from multiprocessing import Pool
from PIL import Image ##调用image库对有反转的图片进行转换
from io import BytesIO
import os #创建文件夹，保存下载好的图片
import multiprocessing

#关于re模块使用的连接https://www.cnblogs.com/shenjianping/p/11647473.html

def url_open(url):
    header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36","Referer": "https://18comic1.one/photo/"}
    req = urllib.request.Request(url,headers=header)
    socket.setdefaulttimeout(5)
    try:
        html= urllib.request.urlopen(req).read()
        return html
    except :
        html=url_open(url)
        return html

def find_next(url):
    html=url_open(url).decode("utf-8")
    next_addrs=list(re.findall(r'<a href="/photo/(.*?)\?"><i class="fa fa-angle-double-right"></i><span>下一話</span></a>',html))
    if(next_addrs!=[]):
        i=int(next_addrs[0])
    else:
        i=0
    return i

def convertImg(img_url):
    
    try:
        fp=open(img_url,'rb')
        img=Image.open(fp)
        img_size = img.size
        img_crop_size = int(img_size[1] / 10)
        img_crop_size_last = (img_size[1] / 10) - img_crop_size  # 解决图片height不能被10整除导致拼接后下方黑条
        img_crop_size_last = round(img_crop_size_last, 1)
        if img_crop_size_last > 0:  # 只有无法整除时才将新建图片进行画布纵向减小
            img_crop_size_last_sum = int(img_crop_size_last * 10)
        else:
            img_crop_size_last_sum = 0
        img_width = int(img_size[0])
        img_block_list = [] #定义一个列表用来存切割后图片
        for img_count in range(10):
            img_crop_box = (0, img_crop_size*img_count, img_width, img_crop_size*(img_count+1))
            img_crop_area = img.crop(img_crop_box)
            img_block_list.append(img_crop_area)
        img_new = Image.new('RGB', (img_size[0], img_size[1]-img_crop_size_last_sum))
        count = 0
        for img_block in reversed(img_block_list):
            img_new.paste(img_block, (0, count*img_crop_size))
            count += 1
        #img_new.show() # 调试显示转化后的图片
        fp.close()
        fp=open(img_url,'wb')
        img_new.save(fp)
        fp.close()
    except Exception as e:
        print(e)

        
def find_resource(url):
    html = url_open(url).decode("utf-8") #获取网页
    print(html)
    img_addrs1= list(re.findall(r'https://cdn-msp.msp-comic1.xyz/media/photos/.*?.jpg',html)) ##改动处
    img_addrs2= list(re.findall(r'https://cdn-msp.18comic1.one/media/photos/.*?.jpg',html))
    img_addrs3= list(re.findall(r'https://cdn-msp.18comic.one/media/photos/.*?.jpg',html))
    img_addrs4= list(re.findall(r'https://cdn-msp.msp-comic.xyz/media/photos/.*?.jpg',html))
    if( img_addrs1!=[]):
        img_addrs=img_addrs1
    if( img_addrs2!=[]):
        img_addrs=img_addrs2
    if( img_addrs3!=[]):
        img_addrs=img_addrs3
    if( img_addrs4!=[]):
        img_addrs=img_addrs4
    if(img_addrs1==[] and img_addrs2==[] and img_addrs3==[] and img_addrs4==[]):
        img_addrs=[]
    print(img_addrs)
    return img_addrs
    

def save_imgs(floder,img_addrs,i):
    t=0
    for each in img_addrs:
        filename = str(i)+"-"+each.split('/')[-1]
        with open(filename,'wb') as f:
            img = url_open(each) #打开图片地址
            f.write(img) #下载图片
            t=t+1
            print("第",t,"张")
            f.close()
            convertImg(floder+filename)
    print("第",i,"个爬取完成，总共",t,"张")

def main(floder='download'): #主程序，传入文件夹名称参数
    url=input()
    i=url.split('/')[-2]
    floder=floder+'/'+url.split('/')[-2]
    os.mkdir(floder)
    os.chdir(floder)
    t=1
    print(url)
    while(i!=0):
        print("解析链接"+str(url))
        img_addrs = find_resource(url)
        if(img_addrs!=[]):
            print("下载图片中")
            save_imgs(floder,img_addrs,t)
            t=t+1
            i=find_next(url)
        else:
            print(i,"不存在")
        time.sleep(10)
if __name__ == '__main__':
    main()
