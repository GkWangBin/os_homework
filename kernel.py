# -*- coding: utf-8 -*-
#!/usr/bin/env python

import ram
import threading
import os

# 本来，中断发生的时候，应该是通过中断向量表跳转到中断处理程序
# 中断处理程序是内核的一部分，但是为了简化问题，内存中没有设置
# 中断向量表，并且事实上，中断向量表在这个模拟程序中也是没作用
# 的，因为貌似没有办法让解释器充当cpu，逐行运行kernel以及其他
# 进程的代码。如果可以做到的话，那当然是最理想了，那样就无需使
# 用多线程、互斥锁等。但现在只能让kernel作为一个线程，循环监听
# 中断信号，如果有中断信号，则开始工作，这看起来就跟现实情况
# 比较相似了。
# 大概就是这个意思：(==表示调度程序运行，_____表示调度程序监听)
# ==_____==_____==__==______==___==......
# 虽然dirty，但还是可以接受的吧

# 其实这个kernel就是传递发现与传递中断信息而已
class KERNEL(object):

    # 动态导入调度算法
    def setsche(self, name):
        self.algo = __import__('algo.'+name, fromlist=[name,])
    
    # 处理中断并调度
    def work(self):
        while True:
            # 简单起见木有打算处理嵌套中断的问题～～
            # 因为可能同时有cpu中断和IO中断，所以加锁在一定程度上防止嵌套中断
            # 不过仍然有可能产生中断覆盖的问题，因为如果IO中断的时刻与cpu中断的
            # 时刻非常接近，那哥也无力回天了。因为调度程序执行时间会相对长一些，
            # 所以还是将中断信息提前获取比较保险，一定程度上防止IO中断的插队
            ram.ram.interlock.acquire()
            inter = ram.ram.inter
            ram.ram.interlock.release()

            # 将发生的中断信息传给调度算法进行决策
            # 中断的处理应该交给调度程序来做
            # 当然调度算法自己根据需要使用内存，不使用传入信息的方法
            if inter is not None:
                self.algo.schedule(inter)
    
    def run(self):
        work = threading.Thread(target = self.work, args = [])
        work.start()

kernel = KERNEL()

