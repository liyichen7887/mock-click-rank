# coding=utf-8
from selenium import webdriver
import requests,time,re
import fake_useragent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import random

tiquApiUrl = 'http://proxy.siyetian.com/apis_get.html?token=gHbi1STq1UeOR1Zx8EVVBjT31STqFUeORUQw0EVRFzTUlENNpXTz0EVJBTTqF1M.gMyETN5AzMxcTM&limit=1&type=0&time=&split=1&split_text='

class Viewer:
    driver_path = "/Users/yichen/Downloads/chromedriver-mac-arm64/chromedriver"     #定义浏览器驱动的位置
    final_url = None

    def __init__(self,kw,title):
        self.bdurl = "https://www.baidu.com/s?wd="
        self.bdurl_base = "https://www.baidu.com/"
        self.kw = kw
        self.title = title
        self.ua=fake_useragent.UserAgent()

    #将request请求返回的cookie转为字符串或者字典形式,默认转为字符串形式
    def handleRequestCookie(self,cookies,type=0):
        cookies_dict =  cookies.get_dict()
        if type==0:
            result = ""
            for index in cookies_dict:
                result = result+"%s=%s; " % (index,cookies_dict[index])
        else:
            result = cookies_dict

        return result


    #先访问百度首页,获取其cookie,再用这个cookie去访问搜索页,这是为了防百度的验证,如果搜索多了就会出现这个验证
    def getBaiduCookie(self):
      
        headers = {"User-Agent":self.ua.random}
        r = requests.get(self.bdurl_base,proxies=proxies,headers=headers)
        self.bdCookies = r.cookies

    #初始化浏览器
    def init_chrome(self, proxies):
        opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}  # 无图模式
        opt.add_experimental_option("prefs",prefs)
        opt.add_argument("user-agent="+self.ua.random)      #添加随机user-agent
        # 使用代理
        proxy = proxies["https"]
        print("IP: ",proxy)
        opt.add_argument(f'--proxy-server={proxy}')
        service = Service(executable_path=self.driver_path)
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=opt)

        self.driver = driver

    # 处理每页获取到的百度搜索,并处理掉里面的html,匹配self.title
    def matchTitle(self,items):
        self.lastItems = items
        for i,item in zip(range(len(items)),items):
            # 获取每个节点的html,去除里面的标签
            html = item.get_attribute("innerHTML")
            html = re.sub("</?[^<>]+>","",html)
            #print(html)
            for t in self.title:
                if html.find(t)!=-1:
                    items[i].click()    #找到则点击链接,并停留1分钟
                    print("Clicked: ", t)
        return False


    # 搜索关键词
    def search(self):
        self.driver.implicitly_wait(10)   # 设置10秒的隐性等待时间
        self.driver.get(self.bdurl_base)
        try:
            self.driver.find_element("xpath", "//input[@id='kw']").send_keys(self.kw)
        except BaseException as e:
            self.driver.find_element("xpath", "//input[@id='index-kw']").send_keys(self.kw)

        try:
            self.driver.find_element("xpath", "//input[@id='su']").click()
        except BaseException as e:
            self.driver.find_element("xpath", "//button[@id='index-bn']").click()


        # 获取每一页的每一条的内容,如果在这一条内容上找到self.title的内容,就获取他的下标
        items = self.driver.find_elements("xpath", "//h3[contains(@class,'t')]/div/a")
        #print(items)
        click_index = self.matchTitle(items)
        time.sleep(10)
        self.driver.quit()    #关闭浏览器
        
        """
        if click_index is False:
            print("click index is false")
            #如果没有找到self.title的内容,就点击下一页重复上面的过程
            while click_index is False:  # is相当于python中的全等于
                #点击下方分页的下一页,如果没有则跳出
                try:
                    self.driver.find_element("xpath", "//div[@id='page']/strong/following-sibling::*[1]").click()
                    time.sleep(2)
                    WebDriverWait(self.driver, 10, 0.5).until(lambda driver:self.driver.find_elements("xpath", "//h3[contains(@class,'t')]/div/a") and self.lastItems!=self.driver.find_elements("xpath", "//h3[contains(@class,'t')]/div/a"))
                    items = self.driver.find_elements("xpath", "//h3[contains(@class,'t')]/div/a")
                    click_index = self.matchTitle(items)

                    if click_index is not False:
                        items[click_index].click()    #找到则点击链接,并停留1分钟
                        time.sleep(60)
                        self.final_url = self.driver.current_url
                        # self.driver.quit()

                        self.res=True    # 最终结果,直接在类外部用对象.res查看最终结果
                except BaseException as e:
                    self.res=False
                    break
        else:
            print("click index is true")
            items[click_index].click()    #找到则点击链接,并停留1分钟
            time.sleep(10)
            self.final_url = self.driver.current_url
            self.res = True  # 最终结果,直接在类外部用对象.res查看最终结果
        """
        



    # 执行搜索,并翻页,找到self.title之后直接点击进去
    def run(self):

        #请求地址 简单提取 具体需要根据实际情况获取 记得添加白名单 http://www.siyetian.com/member/whitelist.html
        apiRes = requests.get(tiquApiUrl,timeout=5)
        ip = apiRes.text
        #代理服务器
        ipport = f'http://{ip}'

        proxies={
            'http':ipport,
            'https':ipport
        }
        
        # 初始化浏览器
        self.init_chrome(proxies)
        time.sleep(2)

        # 请求百度首页,并且输入title,点击搜索
        self.search()

if __name__=="__main__":
    while True:
        key_word=[
            "导热油",
            "高温导热油",
            "低温导热油",
            "载冷剂",
            "合成导热油",
            "超低温导热油"
        ]
        search_title=[
            "导热油300号320号合成350模温机高温导热油夹层夹套",
            "导热油品牌导热油制造专家,国家标准导热油",
            "400度导热油 2023价格表 30年实力厂家",
            "源头实力工厂品牌标杆",
            "导热油全球知名品牌--专注导热油20年",
            "为您量身定做",
            "300度不结焦+定期免费油液检测",
            "适用于零下75℃-230℃之间",
            "超高温合成导热油-低温无硅油",
            "万隆化工有限公司-1桶起售180KG",
            "专注导热油20年",
            "超高温导热油HF15-代替传统硅油-可用于油温400℃以上",
            "导热油生产厂家-万隆化工,源头厂-品质硬-1桶起180KG",
            "WRY导热油泵厂家-武英热油泵导热油厂",
            "适用于零下75℃-230℃之间",
            "超高温合成导热油-低温无硅油",
            "优冷",
            "克拉克",
            "陶普斯",
            "阿姆科",
            "冰河冷媒",
            "曼拓",
            "武英",
            "满足您-100℃-400℃传热需求",
            "代替传统硅油-可用于油温400°C以上",
            "1桶起售180KG",
            "源头工厂-高温可达400度",
            "品牌导热油制造专家,国家标准",
            "无硅油",
            "传热载冷专家",
            "超高温合成",
            "优质导热油源头实力工厂品牌标杆",
            "货比三家不吃亏-联系我们",
            "冷热一体机专用油",
            "高效传热,升温迅速",
            "全球知名品牌--专注",
            "导热油厂家",
            "2024浙江高温",
            "专业厂家 闪点高",
            "30年实力厂家",
            "22年实力厂家",
            "品牌导热油制造专家",
            "安欣和润",
            "l-qc310",
            "节省30%用油成本",
            "厂家直销+品牌润滑油",
            "直达底价",
            "江苏武英热油泵",
            "[克拉克clock导热油]",
            "320度不碳化+品牌润滑油授权经销商",
            "耐高温导热油-低温导热油",
            "世界500强合作企业+全国联仓发货",
            "首诺",
            "Paratherm",
            "山东北方淄特特种油股份有限公司",
            "HD-350-高温导热油L-QC350",
            "舒尔茨导热油公司",
            "中能",
            "生产厂家 售后服务完善",
            "品质保障",
            "欧润克",
            "老客户回购",
            "规格齐全",
            "400°C以上",
            "设备稳定性",
            "制造专家,国家标准"
        ]
        k = random.choice(key_word)
        print("Keyword: ", k)
        # 搜索php教程这个关键词，要点击指定的title的链接，如果这个title在百度没有排名则点击不到
        viewer = Viewer(kw=k,title=search_title)
        viewer.run()
        time.sleep(36)
        print("================================================")
