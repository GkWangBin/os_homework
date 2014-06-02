# -*- coding: utf-8 -*-
#!/usr/bin/env python

from __future__ import print_function

import threading
import time

import cpu
import os
import ram
import sys

"""
0  All attributes off 默认值
1  Bold (or Bright) 粗体 or 高亮
4  Underline 下划线
5  Blink 闪烁
7  Invert 反显
30 Black text
31 Red text
32 Green text
33 Yellow text
34 Blue text
35 Purple text
36 Cyan text
37 White text
40 Black background
41 Red background
42 Green background
43 Yellow background
44 Blue background
45 Purple background
46 Cyan background
47 White background
"""

color = [
            '\x1B[1;37m%s\x1B[0m',
            '\x1B[1;31m%s\x1B[0m',
            '\x1B[1;32m%s\x1B[0m',
            '\x1B[1;33m%s\x1B[0m',
            '\x1B[1;34m%s\x1B[0m',
            '\x1B[1;35m%s\x1B[0m',
            '\x1B[1;36m%s\x1B[0m',
        ]

col = 150
row = 7
cpu_col = 50

FREQ = 0.15

# 申请显存
setattr(ram.ram,'monitable', [[' ']*col for i in range(row)])

class MONITOR(object):
    def work(self):
        while True:
            os.system('clear')
            self.mov()
            self.fresh()
            self.print_tb()
            print('')
            self.print_cpu()
            print('')
            self.print_t()
            time.sleep(FREQ)

    def mov(self):
        for i in range(row):
            for j in range(col-1):
                if j != 0:
                    ram.ram.monitable[i][j] = ram.ram.monitable[i][j+1] 

    def fresh(self):
        pidn = cpu.cpu.pid
        if pidn < 1:
            ram.ram.monitable[0][col-1] = color[0] % '|'
        else:
            ram.ram.monitable[pidn][col-1] = color[pidn] % '|'
        # 结束的进程
        if pidn < 1:
            for i in range(6):
                ram.ram.monitable[i+1][col-1] = ' '
        # 感觉上，应该通过判断进程表来判断一个进程的状态
        # 但是，由于模拟程序的不足，pcb的更新比cpu慢（实
        # 际上应该也是如此），所以现在为了打印效果，直接
        # 根据cpu当前信息来判断，如果运行的是系统进程，
        # 则说明用户进程已被切换或终结
        if pidn > 0:
            ram.ram.monitable[0][col-1] = ' '

    # 打印进程调度过程
    def print_tb(self):
        print(' '*((7+col)/2-9)+'schedule progress')
        print('-'*(8+col-1))
        for i in ram.ram.monitable:
            for j in i:
                print('%s' % j, end='')
            print()
        print('-'*(8+col-1))

    # 打印cpu状态
    def print_cpu(self):
        print(' '*(cpu_col/2-5)+'cpu status')
        print('='*cpu_col)
        pidn = cpu.cpu.pid if cpu.cpu.pid>0 else 0
        print('\t%-10s%s' % ('pid', color[pidn] % str(pidn)))
        print('\t%-10s%s' % ('pc', str(cpu.cpu.pc)))
        print('\t%-10s%s' % ('ra', str(cpu.cpu.ra)))
        print('\t%-10s%s' % ('rb', str(cpu.cpu.rb)))
        print('\t%-10s%s' % ('rc', str(cpu.cpu.rc)))
        print('\t%-10s%s' % ('rd', str(cpu.cpu.rd)))
        print('\t%-10s%s' % ('code', str(cpu.cpu.curcode)))
        print('='*cpu_col)

    # 打印进程号，开始时间，结束时间，服务时间，周转时间，归一化周转时间
    def print_t(self):
        print('  %-10s%18s%25s%20s%20s%20s' % ('pid', 'begin-time', 'end-time', 'served-time', 'turnaround-time', 'Tr/Ts'))
        for i in range(6):
            begtime = ram.ram._oldpro.get('pro'+str(i+1), {}).get('begtime', '-')
            endtime = ram.ram._oldpro.get('pro'+str(i+1), {}).get('endtime', '-')
            exectime = ram.ram._oldpro.get('pro'+str(i+1), {}).get('exectime', '-')
            servedtime = endtime-begtime if (begtime!='-' and endtime!='-') else '-'
            ans = servedtime/exectime if (exectime!='-' and servedtime!='-') else '-'
            print('  %10s%25s%25s%20s%20s%20s' % (color[i+1] % ('pro'+str(i+1)), begtime, endtime, exectime, servedtime, ans))

    # 初始化表格
    def init_monitb(self):
        for i in range(row):
            ram.ram.monitable[i][0] = color[i] % ('  pro'+str(i)+'  ')
        ram.ram.monitable[0][0] = color[0] % 'os/idle '

    def run(self):
        self.init_monitb()
        work = threading.Thread(target = self.work, args=[])
        work.start()


monitor = MONITOR()
