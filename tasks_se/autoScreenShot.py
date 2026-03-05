import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import threading

from tasks_se.core.task import TASK


# AUTOSCREENSHOT 是截取HTML课件每一页的任务
class AUTOSCREENSHOT(TASK):
    AutoScreenShotNums = 0
    _lock = threading.Lock()

    def __init__(self, x_p, y_p, x_s, y_s, u, name=None):
        super().__init__(x_p, y_p, x_s, y_s, u)
        if name is None:
            self.name = f"AUTOSCREENSHOT{AUTOSCREENSHOT.AutoScreenShotNums}"
        else:
            self.name = name
        self.type = "AutoScreenShot"
        try:
            self.dr = self._init_driver()
        except Exception as e:
            raise RuntimeError(f'驱动初始化失败: {e}')
        with AUTOSCREENSHOT._lock:
            AUTOSCREENSHOT.AutoScreenShotNums += 1

    # 自动翻页截屏并保存
    def constant_shot(self):
        saving_path = f"log/{self.type}/results/{self.name}"
        os.makedirs(saving_path, exist_ok=True)
        page_num = int(self.dr.find_element(By.XPATH, '//*[@class="slide-number"]//*[@class="slide-number-b"]').text)
        body = self.dr.find_element(By.TAG_NAME, "body")
        for i in range(1, page_num + 1):
            body.screenshot(f"{saving_path}/page{i}.png")
            body.send_keys(Keys.ARROW_RIGHT)

    # 运行自动化任务
    def run(self):
        self.dr.refresh()
        start_time = time.time()
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        self.constant_shot()
        end_time = time.time()
        time_cost = end_time - start_time
        print(f"开始：{start_time_str} 用时：{time_cost}")
        self.log()
        self.dr.quit()

    def __del__(self):
        super().__del__()


## AUTOSCREENSHOT测试
if __name__ == '__main__':
    folder_path = r"D:\Users\23213\Documents\myDocument\课\bin\R语言"
    for f in os.listdir(folder_path):
        url = "file:///" + os.path.join(folder_path, f)
        name = f.split(".")[0]
        s = AUTOSCREENSHOT(0, 0, 2560, 1440, url, name)
        s.run()
