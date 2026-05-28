from dotenv import load_dotenv
from datetime import datetime, timedelta


from tasks_se import *
from tasks_se.utils.autoFill_utils import *
from tasks_se.utils.threading_utils import threading_running

if __name__ == '__main__':
    ## 多线程测试
    cl_info = get_info("chenliang")
    url1 = "https://www.wjx.top/vm/r0AgKQO.aspx# "
    s1 = AUTOFILL(url1, cl_info, display=True, cover=(0, 0, 400, 800))

    url2 = "https://beta33.pospal.cn"
    load_dotenv()
    un = os.getenv("POSPAL_USERNAME")
    p = os.getenv("POSPAL_PASSWORD")
    s2 = POSPALGETDATA(url2, un, p, display=True, cover=(400, 0, 400, 800))
    s2.set_period("2025-6-1~2025-6-3")

    url3 = "https://beta33.pospal.cn"
    load_dotenv()
    un = os.getenv("POSPAL_USERNAME")
    p = os.getenv("POSPAL_PASSWORD")
    s3 = POSPALGETDATA(url2, un, p)
    s3.set_period("2025-7-1~2025-7-3")

    tml = [s1.run,
           s2.run,
           (s3.run, (), {"task_list": [{"sale": {"verbose": True, "database_url": None}}]})
           ]
    # date = time.strftime("%Y-%m-%d", time.localtime())
    # point = (datetime.now() + timedelta(seconds=1)).strftime("%H:%M:%S")
    # date = "2025-3-31"
    # point = "22:10:00"
    # tml = [(s1.run_with_schedule, (point, date)),
    #        (s2.run_with_schedule, (point, date)),
    #        (s3.run_with_schedule, (point, date),{"task_list":[{"sale": {"verbose": True, "database_url": None}}]})
    #        ]
    threading_running(tml)

    s1.shutdown()
    s2.shutdown()
    s3.shutdown()
