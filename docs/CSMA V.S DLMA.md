# CSMA V.S. DLMA

*Author: ZhankeZhou*

*Version: 1.0*

---

[TOC]



## 1. Attribute Comparison

### 1.1 Action

- 两边的action都为两类，`发`或者`不发`

### 1.2 Channel

- DLMA中，默认为一个channel，暂不支持多个channel
- CSMA中可创建不同channel，测试中使用的是一个channel

### 1.3 State & Node

- DLMA中，state长度为40，nodes数量为2
  - 初始化`state`为全0
  - `next_state`与当前`state`的关系为：
    - `next_state = np.concatenate([state[2:], [agent_action, observation_]])`
    - 也就是说，next_state取state的后38个值，再把当前的`agent_action`和`observation`分别放在第39和第40位，从而构成长度为40的next_state
- CSMA中，state与channel的计时器有关，nodes数量为50
  - state的更新`update_state()`中：`self.state = self.time` 【其含义？】

### 1.4 Oberservation

- DLMA中，oberservation共有四种情况
  -  1   tx, success [*agent success*]
  - -1   tx, no success [*collision*]
  -  2   no tx, success [*aloha success*]
  - -2   no tx, no success [*idle*]
- CSMA中，oberservation未进行相关设置

### 1.5 Optimization Target

- 两边都是最大化throughput

### 1.6 仿真环境交互

- 两边都是用`for loop`模拟真实使用情况
- DLMA中，请查看`environment.py`中的`step`接口
  - 在`step(action, global_time)`中，判断是否发送碰撞，计算各种reward
  - `step()`的返回值为`oberservation`和各种`reward`
- CSMA中，在`node`实例中的`simulate()`接口中计算是否发包，是否发生碰撞，退避多长时间等



## 2. Question List

### 2.1 CSMA

1. `timeout`和`timeout_bar`是如何配合使用的？
2. 相关参数如`difs`或`difs_state`等的具体含义？
3. `channel.state`数值的含义？
4. `update_state()`的含义？

