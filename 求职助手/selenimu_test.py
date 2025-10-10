# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/9 17:51
@Author  : ZhangShenao
@File    : agent.py
@Desc    : 测试selenium无头浏览器抓取
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def web_crawler():
    """网络爬虫"""

    # 指定ChromeDriver可执行程序的路径
    chromedriver_path = (
        "/Users/zsa/apps/chrome-driver/chromedriver-mac-arm64/chromedriver"
    )

    # Chrome浏览器配置
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
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")

    # 创建ChromeDriver实例
    driver = webdriver.Chrome(options=options, service=service)

    # 访问指定网站,获取标题
    driver.get("https://www.baidu.com/")
    print(f"网站标题: {driver.title}")

    # 关闭浏览器
    driver.quit()


if __name__ == "__main__":
    web_crawler()
