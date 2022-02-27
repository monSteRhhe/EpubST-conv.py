import os
import shutil
import sys
import threading
from urllib.robotparser import RobotFileParser
import zipfile
from opencc import OpenCC
from tkinter import *
from tkinter import filedialog


def t2s(epub):
    cc = OpenCC('t2s')

    s_file = cc.convert(os.path.basename(epub)) # 简中文件名(带扩展)
    s_folder = cc.convert(os.path.splitext(s_file)[0]) # 简中文件名(不带扩展)，作文件夹名

    unpack(epub, s_folder)

    # 用OpenCC的命令行处理文件的转换
    for path in getContents(s_folder):
        CCcmd = 'python -m opencc -c t2s -i ' + path + ' -o ' + path
        os.system(CCcmd)

    pack(s_file, os.path.join(os.getcwd(), s_folder))


def s2t(epub):
    cc = OpenCC('s2t')

    t_file = cc.convert(os.path.basename(epub)) # 繁中文件名(带扩展)
    t_folder = cc.convert(os.path.splitext(t_file)[0]) # 繁中文件名(不带扩展)，作文件夹名

    unpack(epub, t_folder)

    # 用OpenCC的命令行处理文件的转换
    for path in getContents(t_folder):
        CCcmd = 'python -m opencc -c s2t -i ' + path + ' -o ' + path
        os.system(CCcmd)

    pack(t_file, os.path.join(os.getcwd(), t_folder))


# 读取文件夹中的转换文件路径
def getContents(folder):
    files_list = [] # 所有子文件路径列表
    for parent, dirnames, filenames in os.walk(folder): # 用os.walk()递归遍历子文件夹
        for file in filenames:
            files_list.append(os.path.join(parent, file))

    match_ext = ['.opf', '.ncx', '.xhtml'] # 需要转换文件的扩展名
    conv_list = [] # 需要转换的文件路径列表
    for file in files_list:
        if os.path.splitext(file)[1] in match_ext:
            conv_list.append(file)

    return conv_list


# 打包epub
def pack(name, folder):
    p = zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED)
    for parent, dirnames, filenames in os.walk(folder):
        no_root = parent.replace(folder, '') # 去除根路径
        for file in filenames:
            p.write(os.path.join(parent, file), os.path.join(no_root, file))
    p.close()

    shutil.rmtree(folder) # 打包完成，删除文件夹


# 解压Epub到文件夹
def unpack(epub, folder):
    unp = zipfile.ZipFile(epub, 'r')
    unp.extractall(folder)
    unp.close()


def isEpub(p):
    if(os.path.splitext(p)[1] == '.epub'):
        return True


class mThread(threading.Thread):
    def __init__(self, mode, epub):
        threading.Thread.__init__(self)
        self.thread_mode = mode # 转换模式
        self.thread_epub = epub # epub路径

    def run(self):
        if(self.thread_mode == '1'):
            t2s(self.thread_epub)
        elif(self.thread_mode == '2'):
            s2t(self.thread_epub)


if __name__ == '__main__':
    if(len(sys.argv) > 1):
        # 拖放文件打开
        input_paths = sys.argv[1:] # 所有输入文件的路径
    else:
        # 直接打开，选择文件
        root = Tk()
        root.withdraw()
        input_paths = filedialog.askopenfilenames(
            title = 'Select Epub Books',
            filetype = [('Epub Books', '*.epub')],
            initialdir = os.getcwd()
        )


    input_epubs = [] # 输入的Epub文件路径
    for p in input_paths:
        if(isEpub(p)):
            input_epubs.append(p)

    print('==========\n 1.繁→简\n 2.简→繁\n==========')
    mode = input('输入数字: ')
    
    threads = [] # 存放线程
    if(mode == '1' or mode == '2'):
        for epub in input_epubs:
            th = mThread(mode, epub)
            threads.append(th)
    else:
        print('INPUT ERROR!')
        input()

    for t in threads:
        t.start()
    for t in threads:
        t.join()
