import time
from selenium.common import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.common.by import By
import threading
from difflib import get_close_matches

from tasks_se.core.task import TASK
from tasks_se.utils.autoFill_utils import *

# AUTOFILL 是填写问卷星的任务
class AUTOFILL(TASK):
    AutoFillNums = 0
    _lock = threading.Lock()
    def __init__(self, x_p, y_p, x_s, y_s, u, info: pd.DataFrame, name=None):
        super().__init__(x_p, y_p, x_s, y_s, u)
        self.info = info
        if name is None:
            self.name = f"AUTOFILL{AUTOFILL.AutoFillNums}"
        else:
            self.name = name
        self.type = "AutoFill"
        try:
            self.dr = self._init_driver()
        except Exception as e:
            raise RuntimeError(f'驱动初始化失败: {e}')
        with AUTOFILL._lock:
            AUTOFILL.AutoFillNums += 1

    # 探测题目页数和每页题数
    def detect(self):
        q_list = []
        page_num = len(self.dr.find_elements(By.XPATH, '//*[@id="divQuestion"]/fieldset'))
        for i in range(1, page_num + 1):
            questions = self.dr.find_elements(By.XPATH, f'//*[@id="fieldset{i}"]/div')
            valid_count = sum(1 for question in questions if question.get_attribute("topic").isdigit())
            q_list.append(valid_count)
        return q_list

    # 判断此题是否填写基础信息
    def searching_basic_info(self, q_current):
        try:
            question = q_current.find_element(By.XPATH, f'./div[1]/div[2]').text.lower()
        except (NoSuchElementException, ElementNotInteractableException):
            print("Fatal Error: Can't find question!!!")
            return None
        df = self.info
        return next((row.info for row in df.itertuples() if row.key in question), None)

    # 填空题实现
    def vacant(self, q_current_num, q_current):
        basic_info = self.searching_basic_info(q_current)
        try:
            blank = q_current.find_element(By.CSS_SELECTOR, f"#q{q_current_num}")
            blank.send_keys()
        except (NoSuchElementException, ElementNotInteractableException):
            print("Fatal Error: Can't find blank!!!")
            return 0
        if basic_info:
            blank.send_keys(basic_info)
            return 1
        else:
            blank.send_keys("无")
            print("This vacant is not related to basic info!!!")
            return 1

    # 单选题实现
    def single(self, q_current):
        basic_info = self.searching_basic_info(q_current)
        try:
            op_num = len(q_current.find_elements(By.XPATH, './div[2]/div'))
            options = [q_current.find_element(By.XPATH, f'./div[2]/div[{i}]/div').text.lower()
                       for i in range(1, op_num+1)]
        except (NoSuchElementException, ElementNotInteractableException):
            print("Fatal Error: Can't find option!!!")
            return 0
        if basic_info:
            matches = get_close_matches(basic_info, options, n=1, cutoff=0.6)
            if matches:
                selection = q_current.find_element(By.XPATH, f'./div[2]//div[text()="{matches[0]}"]')
                if selection.is_displayed() and selection.is_enabled():
                    selection.click()
                    return 1
                else:
                    print("Fatal Error: Can't click selection!!!")
                    return 0
            else:
                selection = q_current.find_element(By.XPATH, './div[2]/div[1]/div')
                print(f"No close option found for '{basic_info}'")
                if selection.is_displayed() and selection.is_enabled():
                    selection.click()
                    return 1
                else:
                    print("Fatal Error: Can't click selection!!!")
                    return 0
        else:
            selection = q_current.find_element(By.XPATH, './div[2]/div[1]/div')
            print("This selection is not related to basic info!!!")
            if selection.is_displayed() and selection.is_enabled():
                selection.click()
                return 1
            else:
                print("Fatal Error: Can't click selection!!!")
                return 0

    # 下拉题实现
    def down_pull(self, q_current_num, q_current):
        basic_info = self.searching_basic_info(q_current)
        try:
            button = q_current.find_element(By.XPATH, './/span[@class="select2-selection__arrow"]')
            button.click()
        except (NoSuchElementException, ElementNotInteractableException):
            print("Fatal Error: Can't find down_pull button!!!")
            return 0
        try:
            op_num = len(self.dr.find_elements(By.XPATH, f'//*[@id="select2-q{q_current_num}-results"]/li')) - 1
            options = [self.dr.find_element
                       (By.XPATH, f'//*[@id="select2-q{q_current_num}-results"]/li[{i}]').text.lower()
                       for i in range(2, 2+op_num)]
        except (NoSuchElementException, ElementNotInteractableException):
            print("Fatal Error: Can't find option!!!")
            return 0
        print(basic_info)
        if basic_info:
            matches = get_close_matches(basic_info, options, n=1, cutoff=0.6)
            if matches:
                selection = (self.dr.find_element
                             (By.XPATH, f'//*[@id="select2-q{q_current_num}-results"]/li[text()="{matches[0]}"]'))
                if selection.is_displayed() and selection.is_enabled():
                    selection.click()
                    return 1
                else:
                    print("Fatal Error: Can't click selection!!!")
                    return 0
            else:
                selection = self.dr.find_element(By.XPATH, f'//*[@id="select2-q{q_current_num}-results"]/li[2]')
                print(f"No close option found for '{basic_info}'")
                if selection.is_displayed() and selection.is_enabled():
                    selection.click()
                    return 1
                else:
                    print("Fatal Error: Can't click selection!!!")
                    return 0
        else:
            selection = self.dr.find_element(By.XPATH, f'//*[@id="select2-q{q_current_num}-results"]/li[2]')
            print("This selection is not related to basic info!!!")
            if selection.is_displayed() and selection.is_enabled():
                selection.click()
                return 1
            else:
                print("Fatal Error: Can't click selection!!!")
                return 0

    # 填写问卷
    def fill(self):
        q_list = self.detect()
        q_current_num = 0
        for j in q_list:
            for k in range(1, j + 1):
                q_current_num += 1
                q_current = self.dr.find_element(By.CSS_SELECTOR, f"#div{q_current_num}")
                q_current_type = q_current.get_attribute("type")
                # 填空题
                if q_current_type == '1' or q_current_type == '2':
                    ret = self.vacant(q_current_num, q_current)
                elif q_current_type == '3':
                    ret = self.single(q_current)
                elif q_current_type == '4':
                    # 问卷报名一般没有多选题， 如果有可能是发布人设置错误， 就当成单选填
                    ret = self.single(q_current)
                elif q_current_type == '7':
                    ret = self.down_pull(q_current_num, q_current)
                else:
                    ret = 0
                    print("other type!!!")
                if not ret:
                    return
                # time.sleep(3)
            try:
                ne = self.dr.find_element(By.CSS_SELECTOR, "#divNext")
                ne.click()
            except (NoSuchElementException, ElementNotInteractableException):
                try:
                    acp = self.dr.find_element(By.XPATH,"//label[@for='checkxiexi']")
                    acp.click()
                    sub= self.dr.find_element(By.CSS_SELECTOR, "#ctlNext")
                    sub.click()
                except (NoSuchElementException, ElementNotInteractableException):
                    print("Fatal Error: Can't find submit button!!!")

    # 运行自动化任务
    def run(self):
        self.dr.refresh()
        start_time = time.time()
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        self.fill()
        end_time = time.time()
        time_cost = end_time - start_time
        print(f"开始：{start_time_str} 用时：{time_cost}")
        time.sleep(1)
        self.shot()
        self.log()
        time.sleep(100)
        self.dr.quit()

    def __del__(self):
        super().__del__()

## AUTOFILL测试
if __name__ == '__main__':
    cl_info = get_info("chenliang")
    if cl_info is not None:
        url1 = "https://www.wjx.top/vm/YDgQxM3.aspx# "
        s1 = AUTOFILL(0, 0, 500, 1440, url1, cl_info)
        # s1.run_with_schedule("18:00:00")
        s1.run()






