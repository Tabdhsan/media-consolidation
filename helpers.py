import time


def timer(func):
    def wrapper(*args, **kwargs):
        st = time.time()
        func(*args, **kwargs)
        et = time.time()
        elapsed_time = et - st
        print("Execution time:", time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

    return wrapper
