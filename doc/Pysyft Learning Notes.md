# Pysyft Learning Notes

*Author: Andrew Zhou*

---

[TOC]

---

## VirtualWorker

- ### 创建VirtualWorker: 

  - `bob = sy.VirtualWorker(hook, id="bob")`
  - `alice = sy.VirtualWorker(hook, id="alice")`

- ### 查看VirtualWorker有几个Tensor: `bob._objects`

  ```
  {29908196729: tensor([1, 2, 3, 4, 5]), 26855181812: tensor([1, 1, 1, 1, 1])}
  ```

- ### Grid

  - A Grid is simply a collection of workers which gives you some convenience functions for when you want to put together a dataset.

    ```python
    workers
    """
    ==>
    [<VirtualWorker id:bob #objects:17>,
     <VirtualWorker id:theo #objects:14>,
     <VirtualWorker id:jason #objects:14>,
     <VirtualWorker id:alice #objects:14>,
     <VirtualWorker id:andy #objects:14>,
     <VirtualWorker id:jon #objects:14>]
     """
     
    grid = sy.PrivateGridNetwork(*workers)
    results = grid.search("#boston")
    ```

    

## Pointers & Tensor

- ### 创建Tensor并发送

  ```python
  x = torch.tensor([1,2,3,4,5])
  y = torch.tensor([1,1,1,1,1])
  
  # 带梯度创建 
  x = torch.tensor([1,2,3,4,5], requires_grad=True)
  # 给tensor附加更多信息
  z = torch.tensor([1,2,3,4,5]).tag("#fun", "#mnist",).describe("The images in the MNIST training dataset.")
  # 可通过z.tags z.description 查看tag和description
  
  # ptr : pointer to Tensor
  x_ptr = x.send(bob)
  y_ptr = y.send(bob)
  ```

- ### Tensor运算

  ```
  z = x_ptr + x_ptr
  # 注意： 创建z会自动地把z发给bob
  ```

- ### 查看pointer的location `x_ptr.location`

  ```
  <VirtualWorker id:bob #objects:2>
  ```

- ### 指向指针的指针 pointer to pointer

  - 此时bob和alice都会新增一个object
  - 用`x.get().get()`可以从bob和alice处取回

  ```python
  x = torch.tensor([1,2,3,4])
  x_ptr = x.send(bob)
  pointer_to_x_ptr = x_ptr.send(alice)
  ```

- ### 指针在worker间移动

  - 背景：x是一个存在于bob处的指针

  ```python
  x = torch.tensor([1,2,3,4,5]).send(bob)
  print('  bob:', bob._objects)
  print('alice:',alice._objects)
  
  ==> 
    bob: {3141456937: tensor([1, 2, 3, 4, 5])}
  alice: {}
  ```

  - 执行 `x = x.move(alice)` ，就把x从bob处移动到了alice处

  ```python
  print('  bob:', bob._objects)
  print('alice:',alice._objects)
  
  ==> 
    bob: {}
  alice: {91756899687: tensor([1, 2, 3, 4, 5])}
  ```

  

## Dataset

- ### 创建迷你数据集

  ```python
  # a toy dataset
  data = torch.tensor([[0,0],[0,1],[1,0],[1,1.]], requires_grad=True)
  target = torch.tensor([[0],[0],[1],[1.]], requires_grad=True)
  
  # send data to workers
  data_bob = data_bob.send(bob)
  data_alice = data_alice.send(alice)
  target_bob = target_bob.send(bob)
  target_alice = target_alice.send(alice)
  
  datasets = [(data_bob,target_bob),(data_alice,target_alice)]
  ```

- ### FederatedDataLoader

  ```python
  # we distribute the dataset across all the workers, it's now a FederatedDataset
  federated_train_loader = sy.FederatedDataLoader( 
      datasets.MNIST('../data', train=True, download=True,
                     transform=transforms.Compose([
                         transforms.ToTensor(),
                         transforms.Normalize((0.1307,), (0.3081,))
                     ]))
      .federate((bob, alice)), 
      batch_size=args.batch_size, shuffle=True, **kwargs)
  ```

  

## Training

- ### 创建模型并发送给worker

  ```python
  model = nn.Linear(2,1)
  
  # Method 1
  model.send(bob)
  
  # Method 2
  bobs_model = model.copy().send(bob)
  ```

- ### 训练过程模板1（不太考虑privacy）

  - 核心内容：把模型发给每个worker，用worker本地的data进行训练，然后回传更新model

  ```python
  # optimizer
  opt = optim.SGD(params=model.parameters(), lr=0.1)
  
  def train():
      # Training Logic
      opt = optim.SGD(params=model.parameters(), lr=0.1)
      for iter in range(10):
          
          # NEW) iterate through each worker's dataset
          for data,target in datasets:
              
              # NEW) send model to correct worker
              model.send(data.location)
  
              # 1) erase previous gradients (if they exist)
              opt.zero_grad()
  
              # 2) make a prediction
              pred = model(data)
  
              # 3) calculate how much we missed
              loss = ((pred - target)**2).sum()
  
              # 4) figure out which weights caused us to miss
              loss.backward()
  
              # 5) change those weights
              opt.step()
              
              # NEW) get model (with gradients)
              model.get()
  
              # 6) print our progress
              print(loss.get()) # NEW) slight edit... need to call .get() on loss\
  ```

- ### Average the Models

  - 把bob和alice的model发给secure_worker，并在其上进行模型平均化处理

  ```python
  alices_model.move(secure_worker)
  bobs_model.move(secure_worker)
  
  with torch.no_grad():
      model.weight.set_(((alices_model.weight.data + bobs_model.weight.data) / 2).get())
      model.bias.set_(((alices_model.bias.data + bobs_model.bias.data) / 2).get())
  ```

- ### 训练过程模板2 使用`federated_train_loader`

  ```python
  def train(args, model, device, federated_train_loader, optimizer, epoch):
      model.train()
      # <-- now it is a distributed dataset
      for batch_idx, (data, target) in enumerate(federated_train_loader): 
          model.send(data.location) # <-- NEW: send the model to the right location
          data, target = data.to(device), target.to(device)
          optimizer.zero_grad()
          
          output = model(data)
          loss = F.nll_loss(output, target)
          loss.backward()
          optimizer.step()
          model.get() # <-- NEW: get the model back
          
          if batch_idx % args.log_interval == 0:
              loss = loss.get() # <-- NEW: get the loss back
              print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                  epoch, batch_idx * args.batch_size, len(federated_train_loader) * args.batch_size,
                  100. * batch_idx / len(federated_train_loader), loss.item()))
  ```

  



## Test / Evaluation

- ### 模板1 

  - 使用`torch.utils.data.DataLoader`而非`sy.FederatedDataLoader`

  ```python
  def test(args, model, device, test_loader):
      model.eval()
      test_loss = 0
      correct = 0
      with torch.no_grad():
          for data, target in test_loader:
              data, target = data.to(device), target.to(device)
              output = model(data)
              # sum up batch loss
              test_loss += F.nll_loss(output, target, reduction='sum').item() 
              # get the index of the max log-probability 
              pred = output.argmax(1, keepdim=True) 
              correct += pred.eq(target.view_as(pred)).sum().item()
  
      test_loss /= len(test_loader.dataset)
  
      print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
          test_loss, correct, len(test_loader.dataset),
          100. * correct / len(test_loader.dataset)))
  ```

  

