import os
import random
import time
import configparser

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
whiteWords = ['救', '治疗', '9', '寄', '奶', '助']
# 以下不用动
# 珈乐超话
globalConfig = {
	'url': 'https://weibo.com/p/1008088498695f86c2878554b54c91018353d4/super_index',
	'prefix': '',
	'suffix': '',
	'sleepTime': 50
}
blackList = []
treatment = []
times = 0


def initConfigFile():
	config = configparser.ConfigParser()
	config.add_section('config')
	config.set('config', 'url', value='https://weibo.com/p/1008088498695f86c2878554b54c91018353d4/super_index')
	config.set('config', 'blackList', value='')
	config.set('config', 'prefix', value='')
	config.set('config', 'suffix', value='')
	config.set('config', 'sleepTime', value='55')
	with open("config.ini", 'w') as configFile:
		config.write(configFile)
	print("初始化配置文件")


def init():
	global globalConfig

	for n in open("comments.txt", 'r', encoding='utf-8').readlines():
		treatment.append(n.replace('\n', ''))
	print("话术加载完成")

	config = configparser.ConfigParser()
	print("加载配置文件")
	if not os.path.exists('config.ini'):
		initConfigFile()
	try:
		config.read("config.ini", encoding='utf-8')
	except FileNotFoundError:
		print("未找到配置文件")
		initConfigFile()
		return
	configList = ['url', 'prefix', 'suffix', 'sleepTime']
	for currConfig in configList:
		try:
			if currConfig == 'sleepTime':
				globalConfig['sleepTime'] = config.getint('config', 'sleepTime')
				continue
			globalConfig[currConfig] = config.get('config', currConfig)
		except Exception:
			print("获取配置项 {:s} 失败.".format(currConfig))

	try:
		tmp = config.get('config', 'blackList').split(',')
		for user in tmp:
			blackList.append(user.strip())
	except Exception:
		print("设置用户黑名单失败.")
	print("配置文件读取完成")


def getTreatment():
	return " ".join([globalConfig['prefix'], random.choice(treatment), globalConfig['suffix']])[:160]


def printWeibo(text):
	tmp = text.split('\n')
	username = tmp[2]
	sendTime = tmp[3].split(' ')[0]
	message = tmp[4]
	comments = tmp[-2].split(' ')[-1]
	approve = tmp[-1].replace('ñ', '')
	if comments.find('评论') != -1:
		comments = 0
	if approve.find('赞') != -1:
		approve = 0
	print('=' * 50)
	print("用户: {} 时间: {}\n{}\n评论: {} 点赞: {}".format(username, sendTime, message, comments, approve))


def weibo_login():
	# 打开微博登录页
	# browser.get('https://passport.weibo.cn/signin/login')
	print("正在获取微博登录页")
	browser.get('https://weibo.com/newlogin')
	browser.implicitly_wait(5)
	# 点击登录
	browser.find_elements(By.CLASS_NAME, "LoginCard_btn_Jp_u1")[0].click()
	# 等待登录页面加载完成，输出二维码
	print("正在获取登录二维码")
	time.sleep(3)
	login_box = browser.find_elements(By.CLASS_NAME, "LoginPop_mabox_3Lyr6")[0]
	login_box.screenshot('login_box.png')
	print("正在打开登录二维码，请在成功扫码登录后关闭二维码图片.")
	os.system("login_box.png")
	while True:
		time.sleep(1)
		if not browser.find_elements(By.CLASS_NAME, "LoginPop_mabox_3Lyr6"):
			print("扫码登录成功.")
			break
		print("判断登录中.")
	return


def skip(text):
	if len(text) > 120:
		# 认为是正常发帖
		return True
	for word in blackWords:
		if text.find(word) != -1:
			return True
	for user in blackList:
		if text.split('\n')[2].find(user) != -1:
			return True
	return False


def shouldHelp(text):
	for word in whiteWords:
		if text.find(word) != -1:
			return True
	return False


def work():
	browser.get(globalConfig['url'])
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
		# print(comments[i].text)
		printWeibo(comments[i].text)
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

	print("\n开始工作")
	comment = comments[minP]
	browser.execute_script("arguments[0].scrollIntoView();", comment)

	try:
		# 点赞
		comment.find_elements(By.CLASS_NAME, "pos")[3].click()
		print("点赞 " + comment.text.split('\n')[2])
		time.sleep(3)
		# 评论
		comment.find_elements(By.CLASS_NAME, "pos")[2].click()
		time.sleep(3)
		# 写入评论
		print("正在模拟手打评论")
		tmp = getTreatment()
		left = right = 0
		while right < len(tmp):
			# 模拟手打
			right = min(len(tmp), right + random.randint(1, 3))
			comment.find_element(By.CSS_SELECTOR, "textarea.W_input").send_keys(tmp[left:right])
			print(tmp[left:right], end='')
			left = right
			time.sleep(random.randint(1, 3) / 5)
		time.sleep(3)
		# 提交评论
		comment.find_element(By.CSS_SELECTOR, "a.W_btn_a").click()
		print("评论\n" + comment.text.split('\n')[2])
	except Exception as e:
		print(e)
		print("尝试评论失败， 可能由于作者设置仅关注可评论")
		time.sleep(3)
		work()


def tip():
	tips = ['欢迎使用小笨蛋也用得来的自动医疗机.', 'powered by selenium.', 'A-SOUL管理层今天出来道歉了吗？']
	for t in tips:
		print(t)


def main():
	init()
	tip()
	weibo_login()

	global times
	while True:
		work()
		times += 1
		print("第{:d}次工作结束，睡眠{}秒.".format(times, globalConfig.get('sleepTime')))
		# 按饭圈指导的说法说隔45s可以免cd，但实际测试的时候45s也会被拿下（可能因为我帐号分数太低了），暂时改为50s，可以自行修改睡眠时间。
		time.sleep(globalConfig.get('sleepTime'))


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
