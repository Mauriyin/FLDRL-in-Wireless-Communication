from random import *

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
        

    # def send_data(self):
    #     if self.channel.time > (self.time):
    #         channel.collision = 1
    #         channel.set_timer(self.channel.time if (self.channel.time) > (self.time + self.frame_len) else (self.time + self.frame_len))
    #     else:
    #         channel.set_timer(self.time + self.frame_len)




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
        self.observation = []
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
        while len(self.ack_time):
            ACK = self.ack_time[0]
            if(ACK == self.time):
                self.ack_time.pop(0)
                return 3
            if(ACK < self.time):
                self.timeout.append(ACK - self.ack_bar + self.timeout_bar)
                self.ack_time.pop(0)
            if(ACK > self.time):
                break
        time_out = 0
        for timeouts in self.timeout:
            if(timeouts != 0 and timeouts <= self.time):
                time_out = 1
                self.timeout.remove(timeouts)

        if time_out:
            if(self.channel.state==0):
                return 5
            else:
                return 4

        if(self.channel.state==0):
            return 2
        else:
            return 1



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
                    #reset backoff/dfis here
                    self.bin_back += 1
                    self.total_pkt_time -= self.frame_len
                    #print(self.send_time)
                else:
                    self.bin_back = 0
                self.backoff = self.binExpBackoff(self.bin_back)  
            return    
        # Detect Channel 
        if(self.channel.state <= self.time):
            if(self.difs_state == 0):
                self.difs_state = 1
                self.collision = 0
                #print("reset difs")
                self.time += self.difs
                return
            else:
                if(self.backoff):
                    self.backoff -= 1
        if(self.backoff == 0):
            #send packet at this slot, so update timer first 
            self.time += 1
            self.send_data()
            self.difs_state = 0
            return
        
        self.time = self.time + 1



    def send_data(self):
        if self.channel.time > (self.time):
            self.channel.collision = 1
            #self.channel.set_timer((self.time + self.frame_len + + self.ack_bar), self.u_id, (self.time + self.frame_len), self.time)
            self.channel.set_timer(self.channel.time if (self.channel.time) > (self.time + self.frame_len + self.ack_bar + 1) else (self.time + self.frame_len + self.ack_bar + 1), self.u_id, (self.time + self.frame_len), self.time)
            self.timeout.append(self.time + self.frame_len + self.timeout_bar)
            #self.time = self.time + self.frame_len + self.timeout_bar
        else:
            self.channel.set_timer((self.time + self.frame_len + self.ack_bar + 1), self.u_id, (self.time + self.frame_len), self.time)
            self.ack_time.append(self.time + self.frame_len + self.ack_bar)
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
# class Ap(Node):
#     """ Access Point Class
    
#     Attributes:
        
#     """