# -*- coding: utf-8 -*-
#!/usr/bin/env python

from Queue import Queue

import cpu
import ram

# 在ram中申请一个队列，作为调度队列
setattr(ram.ram, 'rr_queue', Queue())

'''

轮转调度算法

'''

def schedule(intermsg):

    # rr收到的中断信息有3种

    # 0 = 进程正常退出的exit系统调用
    # 1 = 时间片用完的cpu时钟中断
    # 3 = 新进程加入队列的IO中断

    # 调度前，要抢下中断锁，因为模拟程序是并发的
    # 只能酱紫了，不然可能会导致IO中断与系统调用
    # 的竞争
    ram.ram.interlock.acquire()

    # exit系统调用中断处理
    if intermsg == 0:
        ram.ram.pcblock.acquire()
        index = None
        size = len(ram.ram.pcb)
        # 如果用户进程正常退出，fcfs就去掉pcb项
        # 注意当前已结束进程的cpu状态已经保存在
        # 内存中的缓存
        curpropid = ram.ram.curpro[0]['pid']
        if size != 1:
            for i in range(size):
                if ram.ram.pcb[i]['pid'] == curpropid:
                    index = i
            if index is not None:
                ram.ram.deadpro.append(curpropid)
                del ram.ram.pcb[index]
                # 注意清空缓存
                ram.ram.curpro = []
            else:
                raise Exception('intermsg error!')
            # 然后，就看pcb中是否有下一个进程，有的话
            # 就运行，没有的话，就默认运行idle空进程
            if index < size-1:
                pro = ram.ram.pcb[index]
                cpu.cpu.quickrec(pro['pid'])
            else:
                cpu.cpu.quickrec()
        else:
            pass
        ram.ram.pcblock.release()

    # 调度完后，把中断信息还原为None，释放锁
    ram.ram.inter = None
    ram.ram.interlock.release()

