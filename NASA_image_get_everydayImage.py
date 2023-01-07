# 需要用到的几个模块
import os
import requests
import sys
from tqdm import tqdm

# 主服务器请求函数
def time_try(url_try,params):
    try:
        response = requests.get(url_try,headers=headers,timeout=3,params=params)
    except :
        for i in range(1, 7):
            if i == 6:
                print('请求链接失败，请查看网络连接并重启程序进行重试。')
                os.system('pause')
                sys.exit()
            else:
                try:
                    print('请求链接超时，第{}次重复请求'.format(i))
                    response = requests.get(url_try,headers=headers,timeout=3,params=params)
                    break
                except:
                    continue
    return response

# 获取目标文件大小
def getfile_size(url):
    global file_size
    requests.packages.urllib3.disable_warnings()
    try:
        file_size = int(requests.get(url, timeout=5, stream=True, verify=False, headers=headers).headers['Content-Length'])
        return file_size
    except:
        for con in range(1,7):
            if con == 6:
                print('请求文件失败，请查看网络连接并重启程序进行重试。')
                os.system('pause')
                sys.exit()
            else:
                try:
                    print('请求文件超时，第{}次重新尝试'.format(con))
                    file_size = int(requests.get(url, timeout=5, stream=True, verify=False, headers=headers).headers['Content-Length'])
                    return file_size
                except :
                    continue

# 读取本地文件大小
def getfirst_byte(url,dst):
    global first_byte
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    return first_byte

# 实现下载进度条
def rate(url,dst,header):
    global pbar
    req = requests.get(url, timeout=5, stream=True, verify=False, headers=header)
    pbar = tqdm(
        total=file_size, initial=first_byte,
        unit='B', unit_scale=True, desc='爬取第{}张图片：'.format(pic_dl,),ascii=True)
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return pbar

# 下载链接中断重试
def retry(url,dst):
    for o in range(1,7):
        if o == 6:
            pbar.close()
            goon = noerror('{}\n网络异常，是否继续爬取？\n1、跳过此图片继续爬取\n2、退出程序\n请输入选项1或者2：'.format('-'*30),1,3)
            if goon == 1:
                print('-'*30)
                os.remove(dst)
                return o
            else:
                os.remove(dst)
                sys.exit()
        else:
            try:
                pbar.close()
                print('请求下载异常，第{}次重新请求'.format(o))
                getfirst_byte(url, dst)
                header = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36 Edg/79.0.309.58',
                    "Range": "bytes={}-{}".format(first_byte, file_size)
                    }
                rate(url, dst, header)
                return first_byte
            except:
                continue

# 整个下载流程
def download(url, dst):
    getfile_size(url)
    getfirst_byte(url, dst)
    if first_byte >= file_size:
        print('发现已经完成的图片{}，\n执行下一张图片请求……'.format(url.split('/')[-1]))
        return first_byte
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36 Edg/79.0.309.58',
        "Range": "bytes={}-{}".format(first_byte, file_size)
        }
    try:
        rate(url, dst, header)
    except:
        retry(url, dst)

# 创建下载文件夹目录
def download_path(folder_name):
    folder = '/{}/'.format(folder_name)
    path = os.getcwd() + folder

    if not os.path.exists(path):
        os.makedirs(path)
    return folder_name

#防止输入报错
def noerror(question,range1,range2):
    while True:
        many=input(question)
        if many in str(list(range(range1,range2))):
            number=int(many)
            break
        else:
            print('输入有误，请重新输入！')
            continue
    return number


if __name__ == "__main__":
    url_main = 'https://www.nasa.gov/sites/default/files/'
    url = 'https://www.nasa.gov/api/2/ubernode/_search'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36 Edg/79.0.309.58'}
    page = noerror('请问你想下载NASA多少张最新精选图片(不超过999张)？：',1,1000)
    pic_dl = 0
    params = {
    'size': str(page),
    'from': '0',
    'sort': 'promo-date-time:desc',
    'q': '((ubernode-type:image) AND (routes:1446))',
    '_source_include': 'promo-date-time,master-image,nid,title,topics,missions,collections,other-tags,ubernode-type,primary-tag,secondary-tag,cardfeed-title,type,collection-asset-link,link-or-attachment,pr-leader-sentence,image-feature-caption,attachments,uri',
    }
    print('{}\n正在链接NASA服务器\n{}'.format('-'*30, '-'*30))
    res_nasa = time_try(url, params)
    print('链接服务器成功！\n开始下载NASA精选图片……')
    json_nasa = res_nasa.json()
    url_local_1 = json_nasa['hits']['hits']
    for pic in url_local_1:
        pic_dl+=1
        pic_local = pic['_source']['master-image']['uri']
        url = url_main + pic_local[9:]
        dst = r'{}/{}'.format(download_path('Nasa_Image'), url.split('/')[-1])
        download(url, dst)
    print('全部文件下载完毕，请按任意键退出')
    os.system('pause')
    sys.exit()
