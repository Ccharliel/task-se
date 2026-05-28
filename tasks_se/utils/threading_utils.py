import threading


def threading_running(task_method_list):
    threads = []

    for item in task_method_list:
        if callable(item):
            task_method, args, kwargs = item, (), {}
        elif isinstance(item, tuple):
            if len(item) == 2:
                task_method, args = item
                kwargs = {}
            elif len(item) == 3:
                task_method, args, kwargs = item
            else:
                raise ValueError(
                    "Invalid task format: expected callable, (callable, args), or (callable, args, kwargs)"
                )
        else:
            raise TypeError(
                "Each task must be a callable or a tuple"
            )
        if not callable(task_method):
            raise TypeError("task_method must be callable")
        if not isinstance(args, tuple):
            raise TypeError("args must be a tuple")
        if not isinstance(kwargs, dict):
            raise TypeError("kwargs must be a dict")

        thread = threading.Thread(target=task_method, args=args, kwargs=kwargs)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    # 如果子进程里用了BlockingScheduler，子进程阻塞就不会执行print
    # print("所有子进程结束")