from random import *
from model.DQN import DQN
from config import Config
import numpy as np
from .monteCarlo import reward_mc

class Node():
    """ Basic Class for the nodes in the network
    
    Attributes:
        connection : a list that record the connection to the other nodes
        frame_len : frame length for each transmission frame_len = pkt_size/data_rate
        rate : receiving rate for each user
        channel : input channel for current connection
        time: data time

        observation : observation of the channel
        action : action made at this time slot
        
        
    """

    def __init__(self, connection, frame_len, channel, time, u_id):
        self.connection = connection
        self.frame_len = frame_len
        self.channel = channel
        self.rate = 0
        self.time = time
        self.u_id = u_id
        

class Station(Node):
    """ Station Class
    
    Attributes:
        timeout : timeout for current ACK
        timeout_bar : how long should the packet determine it's timet
        ack_bar : how long when the node can receive ACK
        ack_time : ack arriving time
        send_time : send finish time of each packet 
        observation: {Busy,NoFeedback},{Idle,NoFeedback},{Busy,ACK},{Busy,TimeOut},{Idle,TimeOut}
    """
    def __init__(self, connection, frame_len, channel, time, u_id, timeout_bar, ack_bar):
        Node.__init__(self, connection, frame_len, channel, time, u_id)
        self.timeout_bar = timeout_bar
        self.ack_bar = ack_bar
        self.action = [0]
        self.state = []
        self.ack_time = []
        self.timeout = []
        self.send_time = 0
        self.collision = 0
        self.total_pkt_time = 0

    def send_data(self):
        if self.channel.time > (self.time):
            self.channel.collision = 1
            self.channel.set_timer(self.channel.time if (self.channel.time) > (self.time + self.frame_len) else (self.time + self.frame_len), self.u_id, (self.time + self.frame_len), self.time)
            self.timeout.append(self.time + self.frame_len + self.timeout_bar)
            self.time = self.time + self.frame_len + self.timeout_bar
            self.collision = 1
        else:
            self.channel.set_timer((self.time + self.frame_len), self.u_id, (self.time + self.frame_len), self.time)
            self.ack_time.append(self.time + self.frame_len + self.ack_bar)
            self.time = self.time + self.frame_len + + self.ack_bar
            self.total_pkt_time += self.frame_len
    """
        Decision Maker, will be changed to RL&FL
        
    """

    def decision(self, observation):
        
        if (self.time > self.channel.state):        
            return 1
        else:
            return 0


    def dection(self):
        # detect the channel, observation
        
        # Reveive ACK
        if len(self.ack_time):
            ACK = self.ack_time[0]
            if(ACK == self.time):
                self.ack_time.pop(0)
                self.history[-1][-1] = 'ACK'
                return 'BACK'

        if len(self.timeout):
            timeout = self.timeout[0]
            if(timeout == self.time):
                self.timeout.pop(0)
                self.history[-1][-1] = 'TIMEOUT'
                if(self.channel.state > self.time):
                    return 'BOUT'
                else:
                    return 'IOUT'

        if(self.channel.state > self.time):
            return 'BUSY'
        else:
            return 'IDLE'



    def simulate(self, time):
        if(time < self.time):
            if(time == self.send_time):
                if(self.channel.collision) and (self.collision == 0):
                    self.collision = 1
                    self.time = self.time - self.ack_bar + self.timeout_bar
            return    

        # decision maker
        self.observation.append(self.dection())
        # take action
        if self.decision(self.observation[-1]):
            self.send_data()
        else:
            self.time = self.time + 1
        
        # update information

"""
Note: You can only operate timer once!!!!
"""
class StationDcf(Station):
    """ Station Class
    
    Attributes:
        timeout : timeout for current ACK
        timeout_bar : how long should the packet determine it's timet
        ack_bar : how long when the node can receive ACK
        ack_time : ack arriving time
        send_time : send finish time of each packet 
        observation: {Busy,NoFeedback},{Idle,NoFeedback},{Busy,ACK},{Busy,TimeOut},{Idle,TimeOut}
    """
    def __init__(self, connection, frame_len, channel, time, u_id, timeout_bar, ack_bar, difs, sifs):
        Station.__init__(self, connection, frame_len, channel, time, u_id, timeout_bar, ack_bar)
        self.difs = difs
        self.sifs = sifs
        self.difs_state = 0
        self.backoff = self.binExpBackoff(0)
        self.bin_back = 0
        self.history = []
        self.observation = 'IDLE' #'BACK' 'IDLE' 'BUSY' 'BOUT' 'IOUT'
        self.observation_dict = {'IDLE':0, 'BACK':1, 'BUSY':2, 'BOUT':3, 'IOUT':4}
    
    def simulate(self, time):

        # Wait time, do nothing
        if(time <= self.time):
            # Determine the collison at begining of each transmission (only transmist at the same time could have collision)
            if(time == self.send_time) and (time > 0):
                if(self.channel.collision) and (self.collision == 0):
                    if(self.backoff != 0):
                        print("ERROR! Send Pkt when backoff is not zero")
                    self.collision = 1
                    self.time = self.time - self.ack_bar + self.timeout_bar
                    self.timeout.append(self.time + self.timeout_bar - self.ack_bar )
                    #reset backoff/dfis here
                    self.bin_back += 1
                    self.total_pkt_time -= self.frame_len
                    #print(self.send_time)
                else:
                    self.bin_back = 0
                    self.ack_time.append(self.time)
                self.backoff = self.binExpBackoff(self.bin_back)  
            return    
        # Detect Channel 
        observation = self.dection()
        self.observation = observation
        if(self.channel.state <= self.time):
            if(self.difs_state == 0):
                self.difs_state = 1
                self.collision = 0
                #print("reset difs")
                self.time += self.difs
                self.history.append([observation, 0, 'null'])
                return
            else:
                if(self.backoff):
                    self.backoff -= 1
        if(self.backoff == 0):
            #send packet at this slot, so update timer first 
            self.time += 1
            self.send_data()
            self.difs_state = 0
            self.history.append([observation, 1, 'unknow'])
            return

        self.history.append([observation, 0, 'null'])
        self.time = self.time + 1



    def send_data(self):
        if self.channel.time > (self.time):
            self.channel.collision = 1
            #self.channel.set_timer((self.time + self.frame_len + + self.ack_bar), self.u_id, (self.time + self.frame_len), self.time)
            self.channel.set_timer(self.channel.time if (self.channel.time) > (self.time + self.frame_len + self.ack_bar + 1) else (self.time + self.frame_len + self.ack_bar + 1), self.u_id, (self.time + self.frame_len), self.time)
            #self.timeout.append(self.time + self.frame_len + self.timeout_bar)
            #self.time = self.time + self.frame_len + self.timeout_bar
        else:
            self.channel.set_timer((self.time + self.frame_len + self.ack_bar + 1), self.u_id, (self.time + self.frame_len), self.time)
            #self.ack_time.append(self.time + self.frame_len + self.ack_bar)
            
        self.send_time = self.time + 2
        self.time = self.time + self.frame_len + self.ack_bar
        self.total_pkt_time += self.frame_len


    def binExpBackoff(self,numOfBackoffs):
        if(numOfBackoffs == 0):
            slotsToWait = randint(0, 15)
        elif(numOfBackoffs >=6):
            slotsToWait = randint(0, 1024)
        else:
            slotsToWait = randint(0, (32 * (2 ** (numOfBackoffs-1))))
        return slotsToWait        

class StationRl(Station):
    def __init__(self, connection, frame_len, channel, time, u_id, timeout_bar, ack_bar):
        Station.__init__(self, connection, frame_len, channel, time, u_id, timeout_bar, ack_bar)
        cfg = Config()
        self.history = []
        self.observation = 'IDLE' #'BACK' 'IDLE' 'BUSY' 'BOUT' 'IOUT'
        self.observation_dict = {'IDLE':0, 'BACK':1, 'BUSY':2, 'BOUT':3, 'IOUT':4}
        self.model = DQN()
        self.state = np.zeros(cfg.state_size, int)
        self.decisionCount = 0
        self.action = 0

    def simulate(self, time):

        # Wait time, do nothing
        if(time <= self.time):
            # Determine the collison at begining of each transmission (only transmist at the same time could have collision)

            if(time == (self.time - 1)) and (time > 0):
                # Colliction
                if(self.channel.collision) and (self.collision == 0):
                    self.collision = 1
                    self.timeout.append(self.time + self.timeout_bar - self.ack_bar + 1)
                    #reset backoff/dfis here
                    self.total_pkt_time -= self.frame_len
                    #print(self.send_time)
                # No colliction
                else:
                    self.ack_time.append(self.time+1)
                    #self.channel.time += self.ack_bar 
            return    

        # RL Decision
        self.action = self.model.choose_action(self.state)

        # Calculate Reward
        reward = reward_mc(self.state, self.action, 0.9)
        # reward = randint(0,9)

        # Detect Channel 
        self.observation = self.dection()
        #print(self.observation)
        observation_ = self.observation_dict[self.observation] # change observation to number
        next_state = np.concatenate([self.state[2:], [self.action, observation_]])
        self.model.store_transition(self.state, self.action, reward, next_state)
        self.decisionCount += 1

        if self.decisionCount > 200:
            self.model.learn()

        self.state = next_state

        self.history.append([self.observation, self.action, 'unkonw'])
        if self.action:
            self.collision = 0
            self.send_data()
            
        else:
            self.time = self.time + 1


    def send_data(self):
        if self.channel.time > (self.time):
            self.channel.collision = 1
            #self.channel.set_timer((self.time + self.frame_len + + self.ack_bar), self.u_id, (self.time + self.frame_len), self.time)
            print("step in collision", self.time, self.channel.time)
            self.channel.set_timer(self.channel.time if (self.channel.time) > (self.time + self.frame_len  + self.ack_bar ) else (self.time + self.frame_len + + self.ack_bar ), self.u_id, (self.time + self.frame_len), self.time)
            
            #self.timeout.append(self.time + self.frame_len + self.timeout_bar)
            #self.time = self.time + self.frame_len + self.timeout_bar
        else:
            print("step in send", self.time, self.channel.time)
            self.channel.set_timer((self.time + self.frame_len  + self.ack_bar), self.u_id, (self.time + self.frame_len), self.time)
            #self.ack_time.append(self.time + self.frame_len + self.ack_bar)
            print("after in send", self.time, self.channel.time)
        self.send_time = self.time + 50
        self.time = self.time + self.frame_len + self.ack_bar
        self.total_pkt_time += self.frame_len


    def dection(self):
        # detect the channel, observation
        
        # Reveive ACK
        if len(self.ack_time):
            ACK = self.ack_time[0]
            if(ACK == self.time):
                self.ack_time.pop(0)
                self.history[-1][-1] = 'ACK'
                return 'BACK'

        if len(self.timeout):
            timeout = self.timeout[0]
            if(timeout == self.time):
                self.timeout.pop(0)
                self.history[-1][-1] = 'TIMEOUT'
                if(self.channel.state > self.time):
                    return 'BOUT'
                else:
                    return 'IOUT'

        if(self.channel.state > self.time):
            return 'BUSY'
        else:
            return 'IDLE'
# class Ap(Node):
#     """ Access Point Class
    
#     Attributes:
        
#     """