import random
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
# 简化对edge浏览器的二进制驱动程序的管理
from webdriver_manager.microsoft import EdgeChromiumDriverManager

options = Options()
options.use_chromium = True
options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")
options.add_argument("headless")
browser = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

# 关键词 可自行添加修改
blackWords = ['不要', '不用', '饭圈', '恶心', '请假']
whiteList = ['救', '治疗', '9', '寄', '奶', '助']
# 以下不用动
# 珈乐超话
url = 'https://weibo.com/p/1008088498695f86c2878554b54c91018353d4/super_index'
treatment = []
times = 0


def initTreatment():
    preword = "from 豆瓣 小笨蛋也用得来的自动医疗兵程序 "
    for n in open("comments.txt", 'r', encoding='utf-8').readlines():
        treatment.append(preword + n)
    print("话术加载完成")


def getTreatment():
    return treatment[random.randint(0, len(treatment) - 1)]


def weibo_login():
    # 打开微博登录页
    # browser.get('https://passport.weibo.cn/signin/login')
    browser.get('https://weibo.com/newlogin')
    browser.implicitly_wait(5)
    # 点击登录
    browser.find_elements(By.CLASS_NAME, "LoginCard_btn_Jp_u1")[0].click()
    # 等待登录页面加载完成，输出二维码
    time.sleep(3)
    login_box = browser.find_elements(By.CLASS_NAME, "LoginPop_mabox_3Lyr6")[0]
    login_box.screenshot('login_box.png')
    img = Image.open('login_box.png')
    img.show()
    while True:
        print("等待扫码")
        time.sleep(1)
        if not browser.find_elements(By.CLASS_NAME, "LoginPop_mabox_3Lyr6"):
            print("扫码成功")
            break
    # input("请在成功登录后回车确认")
    return


def skip(text):
    if len(text) > 120:
        # 认为是正常发帖
        return True
    for word in blackWords:
        if text.find(word) != -1:
            return True
    return False


def shouldHelp(text):
    for word in whiteList:
        if text.find(word) != -1:
            return True
    return False


def work():
    browser.get(url)
    browser.implicitly_wait(5)
    time.sleep(3)

    comments = browser.find_elements(By.CLASS_NAME, "WB_cardwrap")[1:]
    while len(comments) == 0:
        browser.implicitly_wait(3)
        comments = browser.find_elements(By.CLASS_NAME, "WB_cardwrap")[1:]
    if len(comments) > 10:
        comments = comments[:10]
    minApprove = 100
    minP = 0
    print("comments length:" + str(len(comments)))
    for i in range(len(comments)):
        print("===========================\n " + comments[i].text)
        if skip(comments[i].text) or not shouldHelp(comments[i].text):
            continue
        if comments[i].text.split("\n")[-2].find('评论') == 1:
            # 优先评论暂无评论的发布
            minP = i
            break
        currApprove = int(comments[i].text.split('\n')[-2].split(' ')[1])
        if currApprove < minApprove:
            minApprove = currApprove
            minP = i

    print("开始治疗 " + str(minP))
    comment = comments[minP]
    browser.execute_script("arguments[0].scrollIntoView();", comment)

    try:
        # 点赞
        comment.find_elements("class name", "pos")[3].click()
        print("点赞 " + comment.text.split('\n')[2])
        time.sleep(3)
        # 评论
        comment.find_elements("class name", "pos")[2].click()
        time.sleep(3)
        # 写入评论
        tmp = getTreatment()
        left = right = 0
        while right < len(tmp):
            # 模拟手打
            right = min(len(tmp), right + random.randint(1, 3))
            comment.find_element(By.CSS_SELECTOR, "textarea.W_input").send_keys(tmp[left:right])
            left = right
            time.sleep(random.randint(1, 3) / 5)
        time.sleep(3)
        # 提交评论
        comment.find_element(By.CSS_SELECTOR, "a.W_btn_a").click()
        print("评论 " + comment.text.split('\n')[2])
    except Exception:
        print("失败， 可能由于作者设置仅关注可评论")
        work()


def main():
    initTreatment()
    weibo_login()

    global times
    while True:
        work()
        times += 1
        print("第{:d}次工作结束，开始睡眠".format(times))
        # 按饭圈指导的说法说隔45s可以免cd，但实际测试的时候45s也会被拿下（可能因为我帐号分数太低了），暂时改为50s，可以自行修改睡眠时间。
        time.sleep(50)


if __name__ == '__main__':
    # try main函数，如果ctrl+c退出，执行except，执行browser.quit()
    try:
        main()
    except KeyboardInterrupt as e:
        print("手动退出")
        print(e)
    except Exception as e:
        print("出错")
        print(e)
    finally:
        print("关闭浏览器")
        browser.quit()
