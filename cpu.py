# -*- coding: utf-8 -*-
#!/usr/bin/env python
from ram import ram

import os
import re
import threading
import time

# 普通指令可见时间为1秒
TIME_PER_INS = 1
# 调度可见时间为0.1秒
TIME_PER_SCH = 0.1

# 正则表达式，模拟赋值操作
ins = re.compile('^(r[a-d]) = ([0-9]+)$')

class CPU(object):

    def __init__(self, slicetime = None):
        # cpu属性常量，分片长度
        self.SLICE_TIME = slicetime
        # cpu寄存器
        self.ra = 0
        self.rb = 0
        self.rc = 0
        self.rd = 0
        # cpu当前的进程
        self.pid = 0
        self.pc = 0
        self.curcode = ' '
        self.pri = -1
        # cpu时钟，用于分片的计时
        self.time = 0

    # 设置分片长度，如果为None则cpu不会分片中断
    def setslice(self, slicetime):
        self.SLICE_TIME = slicetime

    # 为了方便，cpu提供接口快速装载进程信息
    # quickrec的意思大概就是...快速恢复上下文
    def quickrec(self, pid=0, pc=0, ra=0, rb=0, rc=0, rd=0, pri = -1):
        self.pid = pid
        self.pc = pc
        self.ra = ra
        self.rb = rb
        self.rc = rc
        self.rd = rd
        self.pri = pri

    # cpu分片与程序正常结束时中断逻辑
    def work(self):
        while True:
            # 如果当前模式有时钟中断并且时间片用完
            # 如果是idle进程，不切换，因为频繁切换idle
            # 会浪费资源；如果是用户进程，就发生中断
            if self.SLICE_TIME is not None and self.time == self.SLICE_TIME and self.pid != 0:
                # 先保存当前进程的所有cpu状态到内存中的缓存区域
                # 保存的这些信息交给内核处理，cpu只负责保存
                # 之所以要先缓存上下文，是因为内核处理中断可能很快
                # 导致当前进程运行环境被调度程序破坏，所以一定要先保存后中断
                ram.curpro.append(
                    {
                        'pid':self.pid,
                        'pc':self.pc,
                        'ra':self.ra,
                        'rb':self.rb,
                        'rc':self.rc,
                        'rd':self.rd,
                        'curcode':self.curcode,
                        'pri':self.pri,
                    }
                )
                # 计时器重设
                self.time = 0
                # 因为是模拟，所以此处设置当前运行状态为os调度程序
                # -1表示调度程序的进程号
                # 0表示空闲进程idle的进程号
                self.pid = -1
                self.pc = '...'
                self.ra = '...'
                self.rb = '...'
                self.rc = '...'
                self.rd = '...'
                self.curcode = 'kernel_schedule_operation'
                self.pri = -1

                # 为了打印os调度程序的运行效果，故意设置(0.5-TIME_PER_SCH)秒的打印时间
                time.sleep(0.5-TIME_PER_SCH);
                # 发出时钟中断，设置中断标志后，调度程序真正的运行
                self.interrupt(1)
                # 此处给调度程序充分的时间执行(0.1s够了吧)，所以总的认为os调度时间共要TIME_PER_SCH个单位
                # 因为线程的切换很快，所以实际上0.1秒开始不久就已经完成下一个进程的装载了
                time.sleep(TIME_PER_SCH);
                # 好吧现在os的调度程序已经运行完并且完成了上下文的切换
                # cpu可以进入下一个循环了

            # 如果没有启用时间片或者时间片还没完
            else:
                # 那么就继续运行当前的进程，到内存中读取进程控制块中代码区的下一行代码
                ram.pcblock.acquire()
                self.curcode = ram.getcode(self.pid, self.pc)
                ram.pcblock.release()
                # pc++
                self.pc += 1
                self.time += 1
                self.excute(self.curcode)

    # 运行指令
    def excute(self, curcode):
        # 如果当前进程运行完，将当前cpu状态保存到内存的缓存中
        # 然后，则产生中断，告知内核当前进程已经运行完毕
        if curcode == 'exit':
            # 合理上讲，进程发出系统调用exit(0)应该会提前结束时间片
            # 但是，此处为了能打印看到exit语句，所以还是运行1秒吧
            # 并且，为了效果，设置额外的0.5秒给操作系统调度程序展示
            # 但是要先保存原来的状态
            ram.curpro.append(
                {
                    'pid':self.pid,
                    'pc':self.pc,
                    'ra':self.ra,
                    'rb':self.rb,
                    'rc':self.rc,
                    'rd':self.rd,
                    'curcode':self.curcode,
                    'pri':self.pri,
                }
            )
            time.sleep(TIME_PER_INS)

            self.pid = -1
            self.pc = '...'
            self.ra = '...'
            self.rb = '...'
            self.rc = '...'
            self.rd = '...'
            self.curcode = 'kernel_schedule_operation'
            self.pri = -1
            time.sleep(0.5-TIME_PER_SCH)

            # 采用中断将控制交还给操作系统
            self.interrupt(0)
            # 计时器重设
            self.time = 0
            time.sleep(TIME_PER_SCH)

        # 模拟当前代码修改寄存器的功能
        elif curcode[0] == 'r':
            # 使用正则表达式匹配，只粗糙地模拟mov指令
            # 毕竟这个实验重在调度
            ans = ins.findall(curcode)
            # 修改寄存器
            setattr(self, ans[0][0], int(ans[0][1]))
            # 认为每条指令的运行时间为 TIME_PER_INS 秒
            time.sleep(TIME_PER_INS)
        else:
            # 普通指令不处理
            # 认为每条指令的运行时间为 TIME_PER_INS 秒
            time.sleep(TIME_PER_INS)

                
    # cpu中断的api，将内存中的中断标志设置为系统调用或者时间片用完
    def interrupt(self, flag):
        ram.interlock.acquire()
        ram.inter = flag
        ram.interlock.release()

    # 启动cpu
    def run(self):
        work = threading.Thread(target = cpu.work, args = [])
        work.start()

# 初始化的cpu默认不使用分片
cpu = CPU()

# test
if __name__ == '__main__':
    cpu.setslice(5)
    cpu.run()
