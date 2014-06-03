# -*- coding: utf-8 -*-
#!/usr/bin/env python
from threading import Lock

import os
import re
import threading
import time
import Queue

# 简化进程控制块，只包含寄存器、pc、进程号、代码、优先级，其他的不考虑
# 这是空闲进程，如果当前没有可执行进程的话，调度空闲进程运行，用于填充cpu
idle = {'pid':0, 
        'pc':0,
        'ra':'idle', 
        'rb':'idle',
        'rc':'idle',
        'rd':'idle',
        'code':['idle']*100,
        'pri':-1,
        }

class RAM(object):

    def __init__(self):
        # 防止中断标志的竞争，所以对inter加锁
        self.interlock = Lock()
        self.inter = None
        # 进程控制块，为了方便，用数组+字典表示
        # 因为进程控制块需要随时的人为写入进程信息，所以加锁防止竞争
        self.pcblock = Lock()
        self.pcb = [idle, ]
        # 存放死进程号
        self.deadpro = []
        # cpu用于缓存中断前的进程的cpu状态，用数组表示
        self.curpro = []

        # 下边这个字典只是拿来记录已读取进程及其加入时间，防止重复执行
        # 其实将新进程远程调度进ram不应该让ram管，但为了方便
        # 就只能先这样了
        self._oldpro = {}

        # 调度算法数据结构
        self.rr_queue = Queue.Queue()
        self.fb_queues = [Queue.Queue() for i in range(100)]
        self.spn_queue = Queue.PriorityQueue()
        self.srt_queue = Queue.PriorityQueue()

    # 恩，为了方便提供读取进程控制块中相应进程的下一条指令
    def getcode(self, pid, pc):
        for pro in self.pcb:
            if pro['pid'] == pid:
                return pro['code'][pc]

    # 循环查找当前目录下是否有新进程，如果有，加进进程控制块
    # 恩这明显不该让ram来做，只是为了方便
    def searchpro(self):
        pro = re.compile('^pro([0-9]+)$')
        while True:
            proc = False
            files = sorted(os.listdir('./pro/'))
            self.pcblock.acquire()
            for f in files:
                if f[0:3] == 'pro':
                    if f not in self._oldpro.keys():
                        proc = True
                        # 进程一经过远程调度就记录开始时间
                        # 结束时间在exit调用时记录
                        self._oldpro[f] = {'begtime':time.time(),}
                        pid = int(pro.findall(f)[0][0])
                        code = [ins.rstrip() for ins in open('./pro/'+f,'r')]
                        # 进程的服务时间是一定的，由指令数决定，1 s/ins
                        self._oldpro[f]['exectime'] = len(code)
                        self.pcb.append({
                            'pid':pid,
                            'pc':0,
                            'ra':0,
                            'rb':0,
                            'rc':0,
                            'rd':0,
                            'code':code,
                            'pri':0,
                            })

                        # 一有新进程就加进轮转队列
                        self.rr_queue.put(pid)
                        # 一有新进程就加进反馈0队列
                        self.fb_queues[0].put(pid)
                        # 一有新进程就加进spn优先队列（heap）
                        self.spn_queue.put((self._oldpro['pro'+str(pid)]['exectime'], pid))
                        # 一有新进程就加进srt优先队列（heap）
                        self.srt_queue.put((self._oldpro['pro'+str(pid)]['exectime'], pid))

                    else:
                        pass
            self.pcblock.release()
            # IO中断，通知内核有新进程加入，中断编号为3
            if proc:
                self.interlock.acquire()
                self.inter = 3
                self.interlock.release()
            # 设置0.1秒扫描一次目录，太频繁不好...
            time.sleep(0.1)

    # 启动ram，目的是用于扫描目录
    def run(self):
        work = threading.Thread(target = self.searchpro, args = [])
        work.start()

ram = RAM()

# test
if __name__ == '__main__':
    ram.run()
