os_homework
===========

1. 基本的框架已经搭好，目前只要写调度算法
2. 目前完成了`fcfs`,`rr`,`fb`,`spn`,`srt`,`hrrn`
3. 运行方法：

```{sh}
./start algoname slicetime 
```

其中slicetime是可选的，算法需要才设置大小

**eg:**

1. 先来先服务

    ```{sh}
    ./start fcfs
    ```

    ![img](https://github.com/panhzh3/os_homework/raw/master/pic/fcfs.png)


2. 轮转

    ```{sh}
    ./start rr 3
    ```

    ![img](https://github.com/panhzh3/os_homework/raw/master/pic/rr-3.png)


3. 反馈
    ```{sh}
    ./start fb 3
    ```

    ![img](https://github.com/panhzh3/os_homework/raw/master/pic/fb-3.png)

    
4. 最短进程优先
    ```{sh}
    ./start spn
    ```

    ![img](https://github.com/panhzh3/os_homework/raw/master/pic/spn.png)

    
5. 最短剩余优先
    ```{sh}
    ./start srt
    ```

    ![img](https://github.com/panhzh3/os_homework/raw/master/pic/srt.png)
    
6. 最高响应比优先
    ```{sh}
    ./start hrrn
    ```    

    ![img](https://github.com/panhzh3/os_homework/raw/master/pic/hrrn.png)

