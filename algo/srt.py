# -*- coding: utf-8 -*-
#!/usr/bin/env python

import time

from Queue import Queue

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

最短剩余优先

'''

def schedule(intermsg):

    # srt收到的中断信息有3种

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
        # srt_queue显然已经没有该项，不处理
        # 注意当前已结束进程的cpu状态已经保存在内存中的缓存
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

        # 然后，就看srt_queue中是否有用户进程，有的话
        # 出队运行，没有的话，就默认运行idle空进程
        try:
            pid = ram.ram.srt_queue.get_nowait()[1]
        except:
            pid = 0
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
    # 如果是，pass
    # 否则，把当前进程的上下文更新到pcb中，并且计算剩余时间估计，重新入队
    # 最后，出队，恢复pcb中的信息到cpu中
    
    elif intermsg == 3:
        pid = cpu.cpu.pid
        if pid == 0:
            pass
        else:
            pc = cpu.cpu.pc
            ra = cpu.cpu.ra
            rb = cpu.cpu.rb
            rc = cpu.cpu.rc
            rd = cpu.cpu.rd
            
        # 模拟显示系统调度进程
        # 时间还是设置为 TIME_PER_SCH
        cpu.cpu.pid = -1
        cpu.cpu.pc = '...'
        cpu.cpu.ra = '...'
        cpu.cpu.rb = '...'
        cpu.cpu.rc = '...'
        cpu.cpu.rd = '...'
        cpu.cpu.curcode = 'kernel_schedule_operation'
        cpu.cpu.pri = -1

        if pid != 0:
            ram.ram.pcblock.acquire()
            for pro in ram.ram.pcb:
                if pro['pid'] == pid:
                    pro['pc'] = pc
                    pro['ra'] = ra
                    pro['rb'] = rb
                    pro['rc'] = rc
                    pro['rd'] = rd
                    break
            lefttime = ram.ram._oldpro['pro'+str(pid)]['exectime'] - pc + 1
            ram.ram.srt_queue.put((lefttime, pid))
            ram.ram.pcblock.release()

        time.sleep(0.5)

        # 恩将新进程出队
        pid = ram.ram.srt_queue.get_nowait()[1]
        ram.ram.pcblock.acquire()
        for pro in ram.ram.pcb:
            if pro['pid'] == pid:
                pc = pro['pc']
                ra = pro['ra']
                rb = pro['rb']
                rc = pro['rc']
                rd = pro['rd']
                break
        ram.ram.pcblock.release()
        # 注意如果IO中断导致进程切换
        # 则必须重设计时器
        # cpu.cpu.time = 0
        cpu.cpu.quickrec(pid, pc, ra, rb, rc, rd, 0)

    # 调度完后，把中断信息还原为None，释放锁
    ram.ram.inter = None
    ram.ram.interlock.release()

