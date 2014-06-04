# -*- coding: utf-8 -*-
#!/usr/bin/env python

import time

import cpu
import ram

# 临时变量
# 因为没用到优先级，所以无视之
pid = None
pc = None
ra = None
rb = None
rc = None
rd = None

'''

最高响应比优先

'''

def schedule(intermsg):

    # hrrn收到的中断信息有2种

    # 0 = 进程正常退出的exit系统调用
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
        # 如果用户进程正常退出，就去掉pcb项
        # hrrn_queue显然已经没有该项，不处理
        # 注意当前已结束进程的cpu状态已经保存在内存中的缓存
        # 更新pcb表，所有调度算法都一样，通过遍历查找
        curpropid = ram.ram.curpro[0]['pid']
        ram.ram._oldpro['pro'+str(curpropid)]['endtime'] = time.time()
        if size != 1:
            for i in range(size):
                if ram.ram.pcb[i]['pid'] == curpropid:
                    index = i
                    break
            if index is not None:
                ram.ram.deadpro.append(curpropid)
                del ram.ram.pcb[index]
                # 注意清空缓存
                ram.ram.curpro = []
            else:
                raise Exception('intermsg error!')
        ram.ram.pcblock.release()

        # 然后，就看hrrn_queue中是否有用户进程，有的话
        # 全部更新其cpu等待时间，排序，选择最高响应比运行，注意执行出队操作
        # 没有的话，就默认运行idle空进程
        pid = 0
        ram.ram.hrrnlock.acquire()
        if len(ram.ram.hrrn_queue) != 0:
            for pro in ram.ram.hrrn_queue:
                pro[0] = (time.time()-pro[1]+pro[2])/pro[2]
            ram.ram.hrrn_queue.sort()
            pid = ram.ram.hrrn_queue[-1][3]
            del ram.ram.hrrn_queue[-1]
        ram.ram.hrrnlock.release()

        # 取pcb的内容，然后恢复执行（idle除外）
        if pid > 0:
            ram.ram.pcblock.acquire()
            for pro in ram.ram.pcb:
                if pro['pid'] == pid:
                    pc = pro['pc']
                    ra = pro['ra']
                    rb = pro['rb']
                    rc = pro['rc']
                    rd = pro['rd']
            ram.ram.pcblock.release()
            cpu.cpu.quickrec(pid, pc, ra, rb, rc, rd)
        else:
            cpu.cpu.quickrec()

    # IO中断处理
    # 如果有新进程加入，那么就看当前运行的程序是不是idle空闲进程
    # 如果是，那么执行第一个最高响应比的进程
    # 否则，无视
    elif intermsg == 3:
        if cpu.cpu.pid == 0:
            # 恩将最高最高响应比进程出队
            # 同时加进来的多个新进程的响应比相同R = 1
            # 所以实际上不作特别处理，直接取最后一个就行
            ram.ram.hrrnlock.acquire()
            pid = ram.ram.hrrn_queue[-1][3]
            del ram.ram.hrrn_queue[-1]
            ram.ram.hrrnlock.release()
            # 注意如果IO中断导致进程切换
            # 则必须重设计时器
            cpu.cpu.time = 0
            # 因为IO中断提示的是新进程
            # 所以无需读pcb表其他状态
            cpu.cpu.quickrec(pid)
        else:
            pass

    # 调度完后，把中断信息还原为None，释放锁
    ram.ram.inter = None
    ram.ram.interlock.release()

