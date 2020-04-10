import torch                                                                                          
import time
import os
import shutil     
import re
from glob import glob                                                                                       
import torch
torch.multiprocessing.set_sharing_strategy('file_system')     

'''
TODO:
1. add singleton pattern
2. save config to log file
3. add learning rate strategy
4. support muti-GPU
'''
class Config(object):                                                                                
    def __init__(self):
        self.eval_batch_size  =   16
        self.num_workers      =   32
        self.eval_num_workers =   32
        self.USE_CUDA         =   torch.cuda.is_available()                                     
        self.NUM_EPOCHS       =   10000
        self.stationType      =   "RL" # "Dcf" / "RL"

        # Environment Settings
        self.shuffleStationList = True
        self.modelSavePath    =  "./weight/"
        self.saveModel        =  False
        self.loadModel        =  False
        self.allocate_iter    =  200
        self.startAllocationEpoch = 5000

        # DQN Settings
        self.state_size       =  40
        self.n_actions        =  2
        self.memory_size      =  1000
        self.replace_target_iter = 200
        self.batch_size       =  32
        self.learning_rate    =  0.0001
        self.gamma            =  0.9
        self.epsilon          =  1
        self.epsilon_min      =  0.01
        self.epsilon_decay    =  0.995
        self.maxRandomDecisionCount = 50

        # Debug settings
        self.verboseReward    = False
        
        # GPU Settings
        # TODO support muti-GPU
        self.device_ids       =   [0]
        self.main_gpu_id      =   0
        torch.cuda.set_device(self.main_gpu_id)

        # check path
        pathToCheck = [self.modelSavePath]
        for path in pathToCheck:
            if not os.path.exists(path):
                os.mkdir(path)

    # TODO set learning rate strategy
    def get_lr(self,epoch):
        return 0.1
    
    # TODO save all config to log file
    def save_config_to_local_file(self):
        pass

    def getAllConfig(self):
        config_message = "input_size {}, batch_size {}, evaluate_batch_size {}, NUM_EPOCHS {}, lr {}, device_ids {}, ckp_path {}, load_ckp {}".format(self.input_size, self.batch_size, self.evaluate_batch_size, self.NUM_EPOCHS, self.lr, self.device_ids, self.ckp_path, self.load_ckp)
        # print("==> config\n", config_message)
        return config_message
