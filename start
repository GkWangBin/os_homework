#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import cpu
import kernel
import ram
import monitor

SLICE_TIME = [None,]

def main():
    # 调度算法名
    algo = sys.argv[1]
        # 默认分片时间为None，也可以自己设置启用分片
    if len(sys.argv) > 2:
        SLICE_TIME[0] = int(sys.argv[2])
    # 嗯先启动硬件
    # 启动内存
    ram.ram.run()
    # 如果有分片的话，就设置分片时间，否则就是无分片模式
    if SLICE_TIME[0] is not None:
        cpu.cpu.setslice(SLICE_TIME[0])
    cpu.cpu.run()
    # 启动显示器
    monitor.monitor.run()
    # 动态链接调度算法，启动内核
    kernel.kernel.setsche(algo)
    kernel.kernel.run()
    
if __name__ == '__main__':
    main()
