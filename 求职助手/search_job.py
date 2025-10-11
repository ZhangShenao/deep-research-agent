# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/10 10:00
@Author  : ZhangShenao
@File    : search_job.py
@Desc    : 职位搜索
"""

from urllib.parse import urlencode

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import random
import time

# 北京城市代码
BEIJING_CITY_CODE = "101010100"

# 职位列表URL
JOB_SEARCH_URL = "https://www.zhipin.com/web/geek/job?{}"

# User-AGent列表
UA_LIST = [
    # Mac Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.234 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.139 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.140 Safari/537.36",
]

# Cookie字符串
COOKIE_STRING = "ab_guid=97927216-d910-4b84-967f-332c98a67229; lastCity=101010100; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1758850383,1759141048,1759230346,1760059958; HMACCOUNT=8323725EFF9B8906; wt2=DlanWUOXEm54iuCSW97voiqDd6Qod0SbiaeT20HD-uyOkAA4HJig3Dfx5AcF4kXhvhYElDMZCazYsmM3_0o7LdA~~; wbg=0; zp_at=w2U8GHXF1NCCWbldXYJ3sxXa4BuIrZTHjkiwpsCV39w~; __l=l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjobs%3Fcity%3D101010100%26query%3DAgent%25E5%25BC%2580%25E5%258F%2591&r=&g=&s=3&friend_source=0&s=3&friend_source=0; __zp_stoken__=8972fPjvDpsK7wpHCvzgvDwAWCg9CNjs7Klk%2BPi9CPjo%2BOzAwPD47OB5GLknCvsOfXcOjZsOJFUMpOzBDQz5FMD4wGTtEwrxDPTFlwrDDomTDpmHDixLDlsK%2BDX0Kw4nCuyrCpMODD3AsIMOrwr0%2BOUNGe8K5OcOCw7fCvT7DhMOqw4Q7w4c5O0YdKD0LEhRYPTtXTFkLSVtLY2FVCFRVUilGQjwwwonDuCg5EhQNFBUUEg8SFxcVDHp%2FCQsWCw4ADhMOCyg%2BwqLCu8KPxLfDrsSqw6nEnMKaUsKZVcOuwqvDvWHCt2TEgnbCr1jCjMK4wotQTsKpwqfCuFpkwqXCgcK6wrpOwoPCrsKDUFJ1woTCqcOEwr9cw4Jewr9LCBN6CRU6EcOgwq7DgA%3D%3D; __c=1760059958; __a=18554310.1751874177.1759230346.1760059958.767.34.10.759; bst=V2QtkhEub6315gXdJvzxUZLSuw7D3Qxw~~|QtkhEub6315gXdJvzxUZLSuw7DnTxg~~; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1760061424"


def set_user_agent():
    """
    设置浏览器User-Agent
    """

    rand = random.randint(0, len(UA_LIST) - 1)
    return UA_LIST[rand]


def set_cookies(browser: webdriver.Chrome) -> webdriver.Chrome:
    """
    在已登录后的网站页面中获取Cookie信息
    """

    # 拆分cookie字符串为键值对列表
    # 添加cookie
    cookie_pairs = COOKIE_STRING.split("; ")
    for pair in cookie_pairs:
        key, value = pair.strip().split("=", 1)  # cookie字典
        cookie = {"domain": ".zhipin.com", "name": key, "value": value, "path": "/"}
        browser.add_cookie(cookie)
        time.sleep(3)  # 刷新页面
        browser.refresh()
        return browser


def init_driver() -> webdriver.Chrome:
    """
    初始化ChromeDriver
    """

    chromedriver_path = (
        "/Users/zsa/apps/chrome-driver/chromedriver-mac-arm64/chromedriver"
    )
    # '--verbose',  log_output=sys.stdout,
    service = Service(
        executable_path=chromedriver_path,
        service_args=[
            "--headless=new",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
        ],
    )

    options = Options()
    options.add_argument("--headless")  # 采用无头模式
    options.add_argument("--disable-gpu")  # 禁用GPU渲染
    options.add_argument("--incognito")  # 无痕模式
    options.add_argument(
        "--ignore-certificate-errors-spki-list"
    )  # 忽略与证书相关的错误
    options.add_argument("--disable-notifications")  # 禁用浏览器通知和推送API
    options.add_argument(f"user-agent={set_user_agent()}")  # 修改用户代理信息
    options.add_argument("--window-name=huya_test")  # 设置初始窗口用户标题
    options.add_argument("--window-workspace=1")  # 指定初始窗口工作区  #
    options.add_argument("--disable-extensions")  # 禁用浏览器扩展
    options.add_argument("--force-dark-mode")  # 使用暗模式
    options.add_argument(
        "--start-fullscreen"
    )  # 指定浏览器是否以全屏模式启，与进入浏览器后按F11效果相同
    options.add_argument("--start-maximized")
    # options.add_argument("--proxy-server=http://z976.kdltps.com:15818")
    # options.binary_location = path
    driver = webdriver.Chrome(options=options, service=service)

    return driver


def search_job_by_keyword(keyword: str, page: int = 1, size: int = 30) -> str:
    """
    根据关键词搜索职位
    """

    print(f"search job by keyword: {keyword}")

    url = JOB_SEARCH_URL.format(
        urlencode({"query": keyword, "city": BEIJING_CITY_CODE})
    )
    print("url: ", url)
    driver = init_driver()
    if driver is None:
        raise Exception("创建无头浏览器失败")
    print("创建无头浏览器成功")
    # driver.maximize_window()

    driver.get(url)
    print(f"网站标题: {driver.title}")
    # print(driver.get_cookies())
    driver = set_cookies(driver)
    # all_cookies = driver.get_cookies()
    # for cookie in all_cookies:
    #    print(cookie)
    driver.save_screenshot("page_screenshot.png")
    WebDriverWait(driver, 1000, 0.8).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".rec-job-list"))
    )  # 等待页面加载到出现rec-job-list 为止

    li_list = driver.find_elements(By.CSS_SELECTOR, ".rec-job-list li.job-card-box")
    jobs = []
    for li in li_list:
        job_name_list = li.find_elements(By.CSS_SELECTOR, ".job-name")
        if len(job_name_list) == 0:
            continue
        job = {}
        job["job_name"] = job_name_list[0].text
        job_salary_list = li.find_elements(By.CSS_SELECTOR, ".job-salary")
        if job_salary_list and len(job_salary_list) > 0:
            job["job_salary"] = job_salary_list[0].text
        else:
            job["job_salary"] = "暂无"
        job_tags_list = li.find_elements(By.CSS_SELECTOR, ".job-info .tag-list li")
        if job_tags_list and len(job_tags_list) > 0:
            job["job_tags"] = [tag.text for tag in job_tags_list]
        else:
            job["job_tags"] = []
        com_name_list = li.find_elements(By.CSS_SELECTOR, ".boss-name")
        if com_name_list and len(com_name_list) > 0:
            job["com_name"] = com_name_list[0].text
        else:
            continue  #
        com_location_list = li.find_elements(By.CSS_SELECTOR, ".company-location")
        if com_location_list and len(com_location_list) > 0:
            job["com_location"] = com_location_list[0].text.strip()
        else:
            job["com_location"] = "暂无"
        # 获取职位标签（如果有职位icon，比如猎头标识）
        job_tag_icon = li.find_elements(By.CSS_SELECTOR, ".job-tag-icon")
        if job_tag_icon and len(job_tag_icon) > 0:
            job["job_type"] = job_tag_icon[0].get_attribute("alt")
        else:
            job["job_type"] = "直招"
        jobs.append(job)
    driver.close()
    job_tpl = """
{}. 岗位名称: {}
公司名称: {}
工作地点: {}
岗位要求: {}
薪资待遇: {}
职位类型: {}
     """
    ret = ""
    if len(jobs) > 0:
        for i, job in enumerate(jobs):
            job_desc = job_tpl.format(
                str(i + 1),
                job["job_name"],
                job["com_name"],
                job["com_location"],
                ",".join(job["job_tags"]),
                job["job_salary"],
                job["job_type"],
            )
            ret += job_desc + "\n"
        print("完成职位分析")
        return ret
    else:
        raise Exception("没有找到任何职位列表")


if __name__ == "__main__":
    result = search_job_by_keyword(keyword="Agent开发")
    print(result)
