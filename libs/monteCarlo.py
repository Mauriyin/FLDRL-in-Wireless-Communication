'''
state = [c(t-m+1), c(t-m+2), ... , c(t)]
channel = state[-1] = {"action": a, "observation": o}
    a ∈ {"wait", "transmit"}
    o ∈ {"bnf", "inf", "back", "bto", "iot"}
action ∈ {"wait", "transmit"}
reward
'''
reward_transmit_list = []


def reward_mc(state, action, n, result, verbose=False):
    '''
    channel:
    state[-2]: action
    state[-1]: observation
    '''
    channel = [action, state[-1]]
    if action == 0:
        reward = reward_wait(channel, verbose=verbose)
    elif action == 1:
        reward = reward_transmit(state, channel, n, result, verbose=verbose)
    else:
        raise Exception("Undefined action:{}".format(action))
    return reward


def reward_wait(channel, verbose=False):
    # channel["o"] = observation
    # if observation == "bnf" or observation == "back" or observation == "bto":
    #     reward = 1
    # else:
    #     reward = 0
    '''
    observation_dict = {'IDLE':0, 'BACK':1, 'BUSY':2, 'BOUT':3, 'IOUT':4}
    '''
    if channel[1] in [1, 2, 3]:
        reward = 1
    else:
        reward = 0

    if verbose:
        print("in [reward_wait] reward = {}".format(reward))

    return reward


def reward_transmit(state, channel, n, result, verbose=False):
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
    global reward_transmit_list
    channel_list = []
    for i in range(int(len(state) / 2) - 1):
        tmp_action = state[2 * i + 2]
        tmp_observation = state[2 * i + 1]
        tmp_result = result[i]
        if tmp_action == channel[0] and tmp_observation == channel[1]:
            channel_list.append([tmp_action, tmp_observation, tmp_result])

    reward = 0
    for tmp_channel in channel_list:
        if tmp_channel[2] == 1:  # "back"
            # print("Step in BACK!")
            reward = n * reward + 1
        else:
            # print("Step in Nothing!")
            reward = n * reward - 1

    # reward = reward - (-6)
    reward_transmit_list.append(reward)

    if verbose:
        print("[in reward_transmit]: input Channel::{}, state:{}, reward = {}".
              format(channel, state, reward))
        # print("channel_list:", channel_list)
        print("mean of reward_transmit_list: {}".format(
            sum(reward_transmit_list) / len(reward_transmit_list)))

    # return abs(reward)
    return reward
