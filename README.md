# FLDRL-in-Wireless-Communication
- Simulation code for Paper:  
Lyutianyang Zhang<sup>1</sup>
, Hao Yin<sup>1</sup>, Zhanke Zhou, Sumit Roy, Yaping Sun, *Enhancing WiFi Multiple Access Performance with Federated Deep Reinforcement Learning*, VTC2020-Fall.  
<sup>1</sup> *Both authors contribute equally to this work*.  
- Cite our work:
```
@INPROCEEDINGS{FrmaVTC2020,
  author={L. {Zhang} and H. {Yin} and Z. {Zhou} and S. {Roy} and Y. {Sun}},
  booktitle={IEEE 92nd Vehicular Technology Conference (VTC2020-Fall)}, 
  title={Enhancing {WiFi} Multiple Access Performance with Federated Deep Reinforcement Learning}
  }
```
Contributors: Hao Yin, Zhanke Zhou

The paper can be found https://ieeexplore.ieee.org/document/9348485



## Simulations

#### Author Notes:
- Please check `config.py` for model loading and saving setups.

  - ```
    self.saveModel = False
    self.loadModel = True
    ```

- Run `python3 test_CSMA_DQN_withModelAllocation.py` to proceed training.

- `Throughput` is about `5.2`-`5.4`

#### Training log

| Number of Station | Max Avg Throughput | Total training epoch |
| ----------------- | ------------------ | -------------------- |
| 5                 | 5.45               | 10w                  |
| 10                | 5.46               | 13w                  |
| 20                | 5.28               | 22w                  |

