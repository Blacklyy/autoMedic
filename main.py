import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

browser = webdriver.Edge()

# 关键词 可自行添加修改
keywords = ['不要', '不用']
# 以下不用动
# 珈乐超话
url = 'https://weibo.com/p/1008088498695f86c2878554b54c91018353d4/super_index'
treatment = []
times = 0


def initTreatment():
	preword = "提醒求奶不要加超话的tag "
	for n in open("comments.txt", 'r', encoding='utf-8').readlines():
		treatment.append(preword + n)
	print("话术加载完成")


def getTreatment():
	return treatment[random.randint(0, len(treatment) - 1)]


def weibo_login():
	# 打开微博登录页
	# browser.get('https://passport.weibo.cn/signin/login')
	browser.get('https://weibo.com/newlogin')
	# browser.implicitly_wait(5)
	input("请在成功登录后回车确认")
	return


def skip(text):
	if len(text) > 120:
		# 认为是正常发帖
		return True
	for word in keywords:
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
		if skip(comments[i].text):
			# 可以点个赞
			# 不行 点赞也会寄 不点了
			# browser.execute_script("arguments[0].scrollIntoView();", comments[i])
			# print("点赞 " + comments[i].text.split('\n')[2])
			# comments[i].find_elements("class name", "pos")[3].click()
			# 防止频繁操作
			# time.sleep(3)
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

	# 点赞
	comment.find_elements("class name", "pos")[3].click()
	print("点赞 " + comment.text.split('\n')[2])
	time.sleep(3)
	# 评论
	comment.find_elements("class name", "pos")[2].click()
	time.sleep(3)
	# 写入评论
	comment.find_element(By.CSS_SELECTOR, "textarea.W_input").send_keys(getTreatment())
	time.sleep(3)
	# 提交评论
	comment.find_element(By.CSS_SELECTOR, "a.W_btn_a").click()
	print("评论 " + comment.text.split('\n')[2])


def main():
	initTreatment()
	weibo_login()
	# cookie_login()
	global times
	while True:
		work()
		times += 1
		print("第{:d}次工作结束，开始睡眠".format(times))
		# 按饭圈指导的说法说隔45s可以免cd，但实际测试的时候45s也会被拿下，暂时改为60s，还会被拿下的话只能自己增加时间了
		time.sleep(60)


if __name__ == '__main__':
	main()
