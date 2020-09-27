class Channel():
    """ Channel Class
    
    Attributes:
        sate : channel state
        time : current channel time
        frame : current on going frame information: data, connection, ACK
        frame_type : data, control info or ACK
        frame_len : 
        frame_info :
        collision : if two transmission at the same time, collision happens, 
        set to 1       
    """
    def __init__(self, state, frame):
        self.state = state
        self.time = 0
        self.frame = frame
        self.frame_type = None
        self.frame_len = None
        self.frame_info = None
        self.collision = 0
        self.operator = []
        self.start = []
        self.end = []

    def set_timer(self, time, u_id, end_time, start_time):
        if time >= self.time:
            self.operator.append(u_id)
            self.start.append(int(start_time))
            self.end.append(int(end_time))
            self.time = time
        else:
            print(
                "ERROR! Please check time before you reset in the channel!"
            )

    def update_state(self, time):
        self.state = self.time
        if (self.time <= time):
            self.collision = 0

    def set_frame(self, frame_type, length, info):
        self.frame_type = frame_type
        self.frame_len = length
        self.frame_info = info
