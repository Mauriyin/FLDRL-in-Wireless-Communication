'''
state = [c(t-m+1), c(t-m+2), ... , c(t)]
channel = state[-1] = {"action": a, "observation": o}
    a ∈ {"wait", "transmit"}
    o ∈ {"bnf", "inf", "back", "bto", "iot"}
action ∈ {"wait", "transmit"}
reward
'''

def reward_mc(state, action, n):
    channel = state[-1]
    if action == 0:
        reward = reward_wait(channel)
    elif action == 1:
        reward = reward_transmit(state, channel, n)
    else:
        raise Exception("Undefined action!")

def reward_wait(channel):
    # channel["o"] = observation
    # if observation == "bnf" or observation == "back" or observation == "bto":
    #     reward = 1
    # else:
    #     reward = 0

    '''
    observation_dict = {'IDLE':0, 'BACK':1, 'BUSY':2, 'BOUT':3, 'IOUT':4}
    '''
    # TODO Check here
    if channel in [1,2,3]:
        reward = 1
    else:
        reward = 0

    return reward

def reward_transmit(state, channel, n):
    '''
    K = []
    for l, c in enumerate(state):
        if c == cmp(c, channel):
            K.append(l)
        l = 1
    reward = 0
    for k in K:
        if state[k]["observation"] == "back":
            reward = n * reward + 1
        else:
            reward = n * reward - 1
    return reward
    '''

    observation_list = []
    for i in range(int(len(state)/2)):
        tmp_action = state[i]
        tmp_observation = state[2*i]
        if tmp_observation == channel:
            observation_list.append(tmp_observation)

    reward = 0
    for ob in observation_list:
        if ob == 1: # "back"
            #print("Step in BACK!")
            reward = n * reward + 1
        else:
            #print("Step in Nothing!")
            reward = n * reward - 1
    return reward




    