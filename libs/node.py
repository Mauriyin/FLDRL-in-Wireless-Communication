class Node():
    """ Basic Class for the nodes in the network
    
    Attributes:
        connection : a list that record the connection to the other nodes
        frame_len : frame length for each transmission
        rate : receiving rate for each user
        channel : input channel for current connection
        time: data time

        observation : observation of the channel
        action : action made at this time slot
        
        
    """

    def __init__(self, connection, frame_len, channel, time):
        self.connection = connection
        self.frame_len = frame_len
        self.channel = channel
        self.rate = 0
        self.time = time
        self.observation = None
        self.action = None
        

    def send_date(self):
        if self.channel.time > (self.time):
            channel.collision = 1
            channel.set_timer(self.channel.time if (self.channel.time) > (self.time + self.frame_len) else (self.time + self.frame_len))
        else:
            channel.set_timer(self.time + self.frame_len)




class Station(Node):
    """ Station Class
    
    Attributes:
        timeout : timeout for current ACK
        timeout_bar : how long should the packet determine it's timet
        ack_bar
        ack_time
        send_time : send finish time of each packet 
        history time, observation, action, result
        {Busy,NoFeedback},{Idle,NoFeedback},{Busy,ACK},{Busy,TimeOut},{Idle,TimeOut}
    """
    
    
    def send_date(self):
        if self.channel.time > (self.time):
            self.channel.collision = 1
            self.channel.set_timer(self.channel.time if (self.channel.time) > (self.time + self.frame_len) else (self.time + self.frame_len))
            self.timeout.append(self.time + self.frame_len + timeout_bar)
        else:
            channel.set_timer(self.time + self.frame_len)
            self.ack_time.append(self.time + self.frame_len + self.ack_bar)
        self.time = self.time + self.frame_len
    
    """
        Update information, simulation procedure
    """

    def decision(self, observation):
        if (self.channel.sate == 1):
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
                self.timeout.append(ACK - self.ack_bar + timeout_bar)
                self.ack_time.pop(0)
            if(ACK > self.time):
                break
        time_out = 0
        for timeouts in self.timeout:
            if(timeouts <= self.time):
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
            return    

        # decision maker
        self.observation.append(self.dection())
        # take action
        if self.decision():
            send_data()

        # update information

class Ap(Node):
    """ Access Point Class
    
    Attributes:
        
    """