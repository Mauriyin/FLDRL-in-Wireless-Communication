# FLDRL-in-Wireless-Communication
Apply  Deep Reinforcement Learning aided by Federated Learning to Wireless Comunication
## Enhanced CSMA performance using Deep Reinforcement Learning aided by Federated Learning

### Apply Deep RL into FL
#### Solution: Using [Pysyft](<https://github.com/OpenMined/PySyft>)

- PySyft is a Python library for secure and private Deep Learning.
- PySyft decouples private data from model training, using [Federated Learning](https://ai.googleblog.com/2017/04/federated-learning-collaborative.html), [Differential Privacy](https://en.wikipedia.org/wiki/Differential_privacy), and [Multi-Party Computation (MPC)](https://en.wikipedia.org/wiki/Secure_multi-party_computation) within the main Deep Learning frameworks like PyTorch and TensorFlow.
- [Tutorial](<https://github.com/OpenMined/PySyft/tree/master/examples/tutorials>) provides a set of examples on applying RL into FL.

#### Choice A —— Using Google Interface

    - 对深度学习的部分apply FL

#### Choice B —— Develop a Simple Archetechture 
    - 实现一个离散化的架构：各个节点都有一个RL，对于deep learning部分的网络使用FL
    - 中心节点根据不同的方式对deep权重进行调整（直接平均等等）
    - 中心节点返回信息给每个local user进行personal的调整

### Test with Multi-acess paper
    - 可以根据DMRL这篇paper的代码进行修改，应用我们的新架构
    - 测试和效果的对比
    - 可以直接使用论文中的state/action/reward等架构的设计

### CSMA/CA Simulation Integration
    - 调研一些CSMA的简单的simulation的场景
    - 对代码进行重构，形成单独的CSMA仿真的模块，并且提供接口
    - 应用我们的FLDRL框架和新设计的state/action/reward进行实验
