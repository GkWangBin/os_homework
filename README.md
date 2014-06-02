os_homework
===========

1. 基本的框架已经搭好，目前只要写调度算法
2. 目前完成了`fcfs`、`rr`、`fb`，还需要写`spn`，`srt`
3. 运行方法：

```{sh}
python start.py algoname slicetime 
```

其中slicetime是可选的，算法需要才设置大小

**eg:**

1. 先来先服务

    ```{sh}
    python start.py fcfs
    ```

    ![img](https://github.com/panhzh3/os_homework/raw/master/pic/fcfs.png)

2. 轮转

    ```{sh}
    python start.py rr 3
    ```

    ![img](https://github.com/panhzh3/os_homework/raw/master/pic/rr-3.png)

3. 反馈
    ```{sh}
    python start.py fb 3
    ```

    ![img](https://github.com/panhzh3/os_homework/raw/master/pic/fb-3.png)
    
