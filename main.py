from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from datetime import datetime
import warnings, json, os, random, time, requests, threading, re

warnings.filterwarnings("ignore", category=DeprecationWarning) 
def bot(profiles,data):
	min_time = data["min"]
	max_time = data["max"]
	url = json.loads(requests.get(data["url"]).text)
	label = data["label"]
	urls = url[label]
	for bot in profiles:
		headles = data["headless"]
		if (headles != True) and (headles != False):
			headles = False
		options = Options()
		options.headless = headles
		fp = webdriver.FirefoxProfile(f'profile/{bot}')
		fp.set_preference("media.volume_scale", "0.0")
		fp.set_preference('browser.cache.disk.enable', False)
		fp.set_preference('browser.cache.memory.enable', False)
		fp.set_preference('browser.cache.offline.enable', False)
		fp.set_preference('network.cookie.cookieBehavior', 2)
		driver = webdriver.Firefox(options=options,firefox_profile=fp)
		driver.delete_all_cookies()
		try:
			driver.get("https://api.ipify.org/?format=json")
			sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#rawdata-tab").click()
			sleep(1)
			ip_selenium = json.loads(driver.find_element(By.CSS_SELECTOR, ".data").text)["ip"]
			while_repeat = 1
			skip_profile = True
			ip = json.loads(requests.get("http://api.ipify.org/?format=json").text)["ip"]
			while ip == ip_selenium:
				driver.get("https://api.ipify.org/?format=json")
				sleep(1)
				driver.find_element(By.CSS_SELECTOR, "#rawdata-tab").click()
				sleep(1)
				ip_selenium = json.loads(driver.find_element(By.CSS_SELECTOR, ".data").text)["ip"]
				if while_repeat >= 10:
					skip_profile = False
					break
				while_repeat += 1
			if skip_profile:
				urls = random.sample(urls, k=len(urls))
				for url in urls:
					sleep(random.randint(min_time, max_time))
					driver.get(url)
					try:
						element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cookieChoiceDismiss")))
						element.click()
					except Exception as e:
						pass
					sleep(random.randint(min_time, max_time))
					html = driver.find_element(By.XPATH,'//body')
					total_scroled = 0
					page_height = driver.execute_script("return document.body.scrollHeight")
					while total_scroled < page_height:
						html.send_keys(Keys.PAGE_DOWN)
						size = driver.get_window_size()
						total_scroled += size["height"]
						sleep(random.randint(min_time,max_time))
						page_height = driver.execute_script("return document.body.scrollHeight")
					total_scroled = page_height
					sleep(random.randint(min_time,max_time))
					today = datetime.now()
					day = today.strftime("%d-%m-%Y")
					time = today.strftime("%H:%M:%S")
					if os.path.exists("log") == False:
						os.mkdir("log")
					if os.path.exists(f"log/{day}.log") == False:
						with open(f"log/{day}.log","w") as file:
							file.write(f"\n[{time}] Mendapatkan Visit 0\n")
					with open(f"log/{day}.log","r") as file:
						file = file.readlines()
						file = file[len(file)-1].split("Visit ")[1]
						visit = int(file)
					visit += 1
					with open(f"log/{day}.log","a") as file:
						file.write(f"\n[{time}] Mendapatkan Visit {visit}\n")
					print(f"[{time}] Total {visit} Visit")
					requests.get(f"http://rdp.mikdevind.my.id/post.php?label={label}&visit={visit}")
					# print("selesai Visit")
		except Exception as e:
			print(e)
			pass
		driver.delete_all_cookies()
		driver.close()

def split(a, n):
	k, m = divmod(len(a), n)
	return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def main():
	with open("data.json","r") as data_file:
		data = data_file.read()
		data = json.loads(data)
	profiles = data["profile"]
	today = datetime.now()
	day = today.strftime("%d-%m-%Y")
	time = today.strftime("%H:%M:%S")
	if os.path.exists("log") == False:
		os.mkdir("log")
	if os.path.exists(f"log/{day}.log") == False:
		with open(f"log/{day}.log","w") as file:
			file.write(f"\n[{time}] Mendapatkan Visit 0\n")
	with open(f"log/{day}.log","r") as file:
		file = file.readlines()
		file = file[len(file)-1].split("Visit ")[1]
		visit = int(file)
	label = data["label"]
	jmh_threads = int(data["thread"])
	requests.get(f"http://rdp.mikdevind.my.id/post.php?label={label}&visit={visit}")
	profiles = random.sample(profiles, k=len(profiles))
	

	
	
	profiles = list(split(profiles,jmh_threads))
	jobs=[]
	for i in range(jmh_threads):
		p = threading.Thread(target=bot,args=(profiles[i],data))
		p.start()
		jobs.append(p)
	for proc in jobs:
		proc.join()
if __name__ == "__main__":
	while True:
		main()