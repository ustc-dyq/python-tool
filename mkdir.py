import datetime
import os
import random
import string
import argparse
import time
from minio import Minio
from minio.error import S3Error
from shutil import copyfile

# 普通文件读取
class BaseFile:
    dir = ''
    num = 1
    target = ''
    srcName = ''

    def __init__(self, dir, num, target, srcName):
        self.dir = dir
        self.num = num
        self.target = target
        self.srcName = srcName
    
    def createDirs(self):
        start = time.time()
        for i in range(0, self.num):
            now = datetime.datetime.now()
            fileName = os.path.sep + 'SZQ%s0000%d_%s' % (now.strftime("%y-%m%d"),i,''.join(random.sample(string.ascii_letters + string.digits, 8)))
            if os.path.exists(self.dir):
                os.mkdir(self.dir + fileName)
        end = time.time()
        print('create dirs cost:' + str(end - start))
    
    def findDir(self):
        target_list = []
        start = time.time()
        sub_folders = os.listdir(self.dir)
        for sub_folder in sub_folders:
            if sub_folder.find(self.target) != -1:
                 target_list.append(sub_folder)
        end = time.time()
        print("findDir size:%d cost:%s" % (len(target_list), str(end - start)))
        # print(target_list)
        return target_list
    
    def readFile(self):
        start = time.time()
        for dir in self.findDir():
            files = os.listdir(self.dir + os.sep + dir)
            for name in files:
                path = self.dir + os.sep + dir + os.sep + name
                # print('target file path:' + path)
                # f = os.open(path,os.O_RDONLY)
                # line = os.read(f, os.path.getsize(path))
                # os.close(f)
                copyfile(path, name + '_' + ''.join(random.sample(string.ascii_letters + string.digits, 8)))
        end = time.time()        
        print("read file cost:%s" % (str(end - start)))


    def copy(self):
        start = time.time()
        (path, file) = os.path.split(self.srcName)
        for i in range(0, self.num):
            now = datetime.datetime.now()
            newPath = '/SZQ%s0000%d_%s/' % (now.strftime("%y-%m%d"),i,''.join(random.sample(string.ascii_letters + string.digits, 8)))
            if not os.path.exists(newPath):
                os.mkdir(self.dir + newPath)
            copyfile(self.srcName, self.dir + newPath + file)
        end = time.time()
        print("write file num:%d cost:%s" % (self.num, str(end - start)))


# s3访问对象
class S3File(BaseFile):
    accessKey = 'r98Py7pkUwAKWy8v'
    secretKey = 'CaBRrB5IHQM0OFE9mBrtWytaVkTPg8QX'
    endpoint = '192.168.0.167:9000'
    client = None
    def __init__(self, dir, num, target, srcName):
        BaseFile.__init__(self, dir, num, target, srcName)
        self.client = Minio(
             self.endpoint,
             access_key=self.accessKey,
             secret_key=self.secretKey,
             secure = False,
        )

    def createDirs(self):
        start = time.time()
        (path, file) = os.path.split(self.srcName)
        for i in range(0, self.num):
            now = datetime.datetime.now()
            fileName = '/SZQ%s0000%d_%s/%s' % (now.strftime("%y-%m%d"),i,''.join(random.sample(string.ascii_letters + string.digits, 8)),file)
            if self.client.bucket_exists(self.dir):
                self.client.fput_object(
                        self.dir, fileName, self.srcName,
                      )
        end = time.time()
        print("write file num:%d cost:%s" % (self.num, str(end - start)))
    
    def findDir(self):
        target_list = []
        start = time.time()
        sub_folders = self.client.list_objects(
                      self.dir, prefix=self.target, recursive=True,
        )
        for sub_folder in sub_folders:
            target_list.append(sub_folder.object_name)
        end = time.time()
        print("findDir size:%d cost:%s" % (len(target_list), str(end - start)))
        # print(target_list)
        return target_list
    
    def readFile(self):
        start = time.time()
        for name in self.findDir():
            # print('target file path:' + name)
            (path, file) = os.path.split(name)
            destName = file + '_' + ''.join(random.sample(string.ascii_letters + string.digits, 8))
            res = self.client.fget_object(self.dir,name,destName)
            # print('target file size:' + str(os.path.getsize(destName)))
        end = time.time()
        print("read file cost:%s" % (str(end - start)))
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Create n files')
    parser.add_argument("-n", "--num", action="store", default=5000, type=int, help='创建n个文件夹或者写入n个文件')
    parser.add_argument("-d", "--dir", action="store", default='/opt/test', help='网盘的文件路径，s3则是对应的桶')
    parser.add_argument("-t", "--target", action="store", help='指定查询的目标文件夹名称（模糊匹配，S3则是前缀匹配）')
    parser.add_argument("-s", "--select", action="store", default=1, type=int, help='选择操作类型，1是创建n个文件夹，2是查询指定目录,3是创建文件，4 是s3创建文件，5是s3查询,6是readfile,7是s3的readfile')
    parser.add_argument("-src", "--srcName", action="store", help='上传的源文件路径')
    args = parser.parse_args()
    print(args)
    file = BaseFile(args.dir, args.num, args.target, args.srcName)
    s3File = S3File(args.dir, args.num, args.target, args.srcName)
    if 1 == args.select:
        file.createDirs()
    elif 2 == args.select:
        file.findDir()
    elif 3 == args.select:
        file.copy()
    elif 4 == args.select:
        s3File.createDirs()
    elif 5 == args.select:
        s3File.findDir()
    elif 6 == args.select:
        file.readFile()
    elif 7 == args.select:
        s3File.readFile()