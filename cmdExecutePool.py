from concurrent.futures import ThreadPoolExecutor
import threading
import time
import subprocess
import argparse

def task(num, command):
    start = time.time()
    subprocess.call(command.split(' '))
    end = time.time()
    print('Thread ' + str(num) + ' cost:' + str(end - start))

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Create n files')
    parser.add_argument("-cmd", "--command", action="store", help='并发执行的命令，用单空格隔开')
    parser.add_argument("-n", "--num", action="store", default=1, type=int, help='并发的数量')
    args = parser.parse_args()
    print(args)
    pool = ThreadPoolExecutor(max_workers=args.num)
    for i in range(0,args.num):
        pool.submit(task,i,args.command)