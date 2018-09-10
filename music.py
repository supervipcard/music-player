# -*- coding: utf-8 -*-

import threading
from tkinter import *
from parse import *
import sqlite3
import pyglet
import time
import os
import random
from song_Transform import *


def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)


def surface():
    threads = []

    # 设计GUI界面
    root = Tk()
    root.resizable(False, False)
    root.title('音乐播放器')
    center_window(root, 440, 600)

    frame0 = Frame(root, width=440, height=40)
    frame0.grid(row=0, column=0)
    frame0.grid_propagate(0)
    label = Label(frame0, text='Music Player', font='Helvetica -20 bold')
    label.grid(row=0, column=0)

    frame1 = Frame(root, width=440, height=30)
    frame1.grid(row=1, column=0)
    frame1.grid_propagate(0)
    research_label = Label(frame1, text='音乐搜索：')
    research_label.grid(row=0, column=0)
    entry = Entry(frame1, text="0")
    entry.grid(row=0, column=1)
    bb = Button(frame1, text="确定", bg='white', width=5, height=1)
    bb.grid(row=0, column=2, padx=10)

    def chose1():
        bb['command'] = hunt1    # 通过歌曲搜索

    def chose2():
        bb['command'] = hunt2    # 通过歌手搜索

    frame2 = Frame(root, width=320, height=25)
    frame2.grid(row=2, column=0)
    frame2.grid_propagate(0)
    var = IntVar()
    rb1 = Radiobutton(frame2, text="歌曲", variable=var, value=1, command=chose1)
    rb2 = Radiobutton(frame2, text="歌手", variable=var, value=2, command=chose2)
    rb1.grid(row=0, column=0)
    rb2.grid(row=0, column=1)

    frame3 = Frame(root, width=200, height=40)
    frame3.grid(row=3, column=0, sticky=W)
    frame3.grid_propagate(0)
    play_label = Label(frame3, text='安静地听首歌是一种享受！')
    play_label.grid(row=0, column=0)

    frame4 = Frame(root, width=250, height=40)
    frame4.grid(row=3, column=0, sticky=E)
    frame4.grid_propagate(0)
    label_rate = Label(frame4, text='播放进度')
    label_rate.grid(row=0, column=0)
    progress_scale = Scale(frame4, orient=HORIZONTAL, showvalue=0, length=180)
    progress_scale.grid(row=0, column=1)

    frame5 = Frame(root, width=80, height=50)
    frame5.grid(row=4, column=0, sticky=W, padx=30)
    frame5.grid_propagate(0)
    s1 = PhotoImage(file='a.gif')
    s2 = PhotoImage(file='b.gif')
    s3 = PhotoImage(file='c.gif')
    bb1 = Button(frame5, image=s1, height=20, width=20, relief=RAISED)
    bb2 = Button(frame5, image=s2, height=20, width=20, relief=RAISED)
    bb3 = Button(frame5, image=s3, height=20, width=20, relief=RAISED)
    bb1.grid(row=0, column=0)
    bb2.grid(row=0, column=1)
    bb3.grid(row=0, column=2)

    frame6 = Frame(root, width=100, height=50)
    frame6.grid(row=4, column=0, sticky=N)
    frame6.grid_propagate(0)
    b1 = Button(frame6, text="▶", bg='blue', width=3)
    b2 = Button(frame6, text="■", bg='blue', width=3)
    b1.grid(row=0, column=0)
    b2.grid(row=0, column=1)

    frame7 = Frame(root)
    frame7.grid(row=5, column=0)
    frame7.grid_propagate(0)
    scrollbar = Scrollbar(frame7)
    scrollbar.pack(side=RIGHT, fill=Y)
    mylist = Listbox(frame7, height=21, width=60, yscrollcommand=scrollbar.set)
    mylist.pack()
    curs.execute("SELECT * FROM catalog")
    rows = curs.fetchall()
    for i in rows:
        mylist.insert(END, str(i[0]) + '  ' + i[1] + '  ' + i[2])
    scrollbar.config(command=mylist.yview)    # 将数据库中的所有歌曲嵌入到界面上，并设置滚动条

    frame8 = Frame(root, width=170, height=50)
    frame8.grid(row=4, column=0, sticky=E)
    frame8.grid_propagate(0)
    sound_label = Label(frame8, text='音量：')
    sound_label.grid(row=0, column=0)
    scale = Scale(frame8, from_=0, to=100, orient=HORIZONTAL)
    scale.set(100)
    scale.grid(row=0, column=1)

    frame9 = Frame(root, width=120, height=50)
    frame9.grid(row=6, column=0, sticky=E)
    frame9.grid_propagate(0)
    my_label = Label(frame9, text='项晨专属音乐播放器', pady=8)
    my_label.grid(row=0, column=0)

    frame10 = Frame(root, width=150, height=50)
    frame10.grid(row=6, column=0, sticky=W)
    frame10.grid_propagate(0)
    mode_label = Label(frame10, text='当前播放模式：顺序播放', pady=8)
    mode_label.grid(row=0, column=0)

    def hunt1():
        mylist.delete(0, mylist.size() - 1)
        for j in rows:
            if entry.get() in j[1]:
                mylist.insert(END, str(j[0]) + '  ' + j[1] + '  ' + j[2])

    def hunt2():
        mylist.delete(0, mylist.size() - 1)
        for j in rows:
            if entry.get() in j[2]:
                mylist.insert(END, str(j[0]) + '  ' + j[1] + '  ' + j[2])

    class TestThread(threading.Thread):
        def __init__(self):
            super().__init__()
            self.player = pyglet.media.Player()
            self.song_time = 0
            self.sign = 3
            self.next_item = 1
            self.position = 0
            self.__running = 1
            self.stop_sign = 0
            scale.set(100)
            mode_label['text'] = '当前播放模式：顺序播放'

        def run(self):
            song = mylist.get(mylist.curselection()).split('  ')[1]
            play_label['text'] = '正在播放：' + song
            conn1 = sqlite3.connect('song_data.db')
            curs1 = conn1.cursor()
            curs1.execute("SELECT * FROM catalog WHERE song=?", (song,))
            row1 = curs1.fetchone()
            self.song_time = parse(song, row1[4] + 'mmm')   # 解析并下载音乐
            if row1[0] < len(rows):
                self.next_item = row1[0] + 1

            if os.path.exists(song + '.mp3'):
                transform(song)
                if os.path.exists(song + '(Y)' + '.mp3'):
                    music = pyglet.media.load(song + '(Y)' + '.mp3')
                else:
                    music = pyglet.media.load(song + '.mp3')   # 加载音乐
                self.player.queue(music)
                self.player.play()  # 播放音乐

            progress_scale['from_'] = 0
            progress_scale['to'] = self.song_time
            progress_scale.set(0)
            progress_scale.bind('<Button-1>', self.ahead)
            progress_scale.bind('<ButtonRelease-1>', self.again)  # 进度条初始设置
            b1['command'] = self.gostart
            b2['command'] = self.stop
            scale['command'] = self.sound
            bb1['command'] = self.shuffle
            bb2['command'] = self.repeat_once
            bb3['command'] = self.all_repeat

            while self.__running:
                time.sleep(1)
                if self.stop_sign == 0:
                    self.position += 1
                    progress_scale.set(self.position)

                if self.position > self.song_time + 1:  # 一首歌放完之后
                    if self.sign == 1:   # 随机播放
                        curs1.execute("SELECT * FROM catalog WHERE item=?", (random.randint(1, len(rows)),))
                        row2 = curs1.fetchone()
                        self.song_time = parse(row2[1], row2[4] + 'mmm')

                        if os.path.exists(row2[1] + '.mp3'):
                            transform(row2[1])
                            if os.path.exists(row2[1] + '(Y)' + '.mp3'):
                                new_music = pyglet.media.load(row2[1] + '(Y)' + '.mp3')
                            else:
                                new_music = pyglet.media.load(row2[1] + '.mp3')
                            play_label['text'] = '正在播放：' + row2[1]

                            self.player.queue(new_music)
                            self.player.next_source()
                            self.position = 0
                            progress_scale.set(self.position)
                            progress_scale['to'] = self.song_time

                    elif self.sign == 2:   # 单曲循环
                        self.player.seek(0)
                        self.player.play()
                        self.position = 0
                        progress_scale.set(self.position)

                    elif self.sign == 3:   # 顺序播放
                        curs1.execute("SELECT * FROM catalog WHERE item=?", (self.next_item,))
                        row3 = curs1.fetchone()
                        self.song_time = parse(row3[1], row3[4] + 'mmm')
                        if self.next_item < len(rows):
                            self.next_item += 1
                        else:
                            self.next_item = 1

                        if os.path.exists(row3[1] + '.mp3'):
                            transform(row3[1])
                            if os.path.exists(row3[1] + '(Y)' + '.mp3'):
                                new_music = pyglet.media.load(row3[1] + '(Y)' + '.mp3')
                            else:
                                new_music = pyglet.media.load(row3[1] + '.mp3')
                            play_label['text'] = '正在播放：' + row3[1]

                            self.player.queue(new_music)
                            self.player.next_source()
                            self.position = 0
                            progress_scale.set(self.position)
                            progress_scale['to'] = self.song_time

        def sound(self, ev=None):
            self.player.volume = scale.get() / 100
            return

        def shuffle(self):
            self.sign = 1
            mode_label['text'] = '当前播放模式：随机播放'
            return

        def repeat_once(self):
            self.sign = 2
            mode_label['text'] = '当前播放模式：单曲循环'
            return

        def all_repeat(self):
            self.sign = 3
            mode_label['text'] = '当前播放模式：顺序播放'
            return

        def stop(self):
            self.stop_sign = 1
            self.player.pause()
            return

        def gostart(self):
            self.stop_sign = 0
            self.player.play()
            return

        def ahead(self, event):
            self.stop()
            return

        def again(self, event):
            self.position = progress_scale.get()
            self.player.seek(progress_scale.get())
            self.gostart()
            return

        def stop_thread(self):
            self.__running = 0
            return

    def thread(event):
        if len(threads) == 0:   # 首次播放
            p = TestThread()   # 开启一个线程
            p.setDaemon(True)
            threads.append(p)   # 加入线程列表
            p.start()

        elif len(threads) == 1:   # 切歌
            threads[0].player.delete()   # 停止前一个线程的歌曲播放
            threads[0].stop_thread()
            threads.pop(0)   # 将前一个线程移出线程列表
            p = TestThread()   # 开启一个新线程
            p.setDaemon(True)
            threads.append(p)   # 将新线程加入线程列表
            p.start()

    mylist.bind('<Double-Button-1>', thread)   # 双击播放音乐
    root.mainloop()


def main():
    surface()


if __name__ == '__main__':
    conn = sqlite3.connect('song_data.db')
    curs = conn.cursor()
    main()
