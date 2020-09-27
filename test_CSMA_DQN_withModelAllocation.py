import random
from libs.node import Node
from libs.node import Station
from libs.node import StationDcf
from libs.node import StationRl
from libs.channel import Channel
from tqdm import tqdm
from config import Config
from libs.allocateModel import Allocator

import matplotlib.pyplot as plt
import pylab as pl
from mpl_toolkits.axes_grid1 import host_subplot

cfg = Config()
global_time = 0
channel = Channel(global_time, [])

station_num = 5
data_rate = 6  # Mbps
# All the lengeth is a mutible of slot

# incule header
pkt_len = 1560
# us
slot_len = 10
sifs = 2
ack_len = 2 + sifs
difs = 4
timeout = ack_len

frame_len = pkt_len * 8 / slot_len / data_rate
stations_list = []
total_time = 0

for i in range(station_num):
    if cfg.stationType == "Dcf":
        station = StationDcf(i, frame_len, channel,
                             global_time, i, timeout, ack_len, difs, sifs)
    elif cfg.stationType == "RL":
        station = StationRl(i, frame_len, channel,
                            global_time, i, timeout, ack_len, (i+1))
    stations_list.append(station)

allocator = Allocator(stations_list, cfg.modelSavePath)

if cfg.stationType == "Dcf":
    startEpoch = 0
elif cfg.stationType == "RL":
    startEpoch = stations_list[0].epoch

print("==> startEpoch: ", startEpoch)
for i in tqdm(range(startEpoch, startEpoch+cfg.NUM_EPOCHS)):
    for station in stations_list:
        station.simulate(global_time)
    global_time = global_time + 1
    channel.update_state(global_time)

    if cfg.shuffleStationList:
        random.shuffle(stations_list)

    if i % cfg.allocate_iter == 0 and i > startEpoch+cfg.startAllocationEpoch:
        allocator.allocateModel()

for station in stations_list:
    total_time += station.total_pkt_time
    if cfg.saveModel and cfg.stationType == "RL":
        station.saveModel()
if cfg.saveModel:
    allocator.saveBestModel()

print("==> total_time:", total_time)
total_time_channel = 0

# if(i > 0):
#     if ((channel.start[i] - channel.start[i-1]) < frame_len):
#         continue
# if(i < (len(channel.start)-1)):
#     if(channel.start[i] - channel.start[i+1]) < frame_len:
#         continue

for i in range(len(channel.start)):
    # if(i > 0):
    #     if ((channel.start[i] - channel.end[i-1]) < 4):
    #         continue
    if(i > 0):
        if ((channel.start[i] - channel.start[i-1]) < frame_len):
            continue
    total_time_channel += frame_len

print("==> total_time_channel:", total_time_channel)
print("==> channel time:", channel.time)

try:
    throughput = total_time/channel.time * data_rate * 1500 / 1560
    print("==> throughput:", throughput)
except:
    print("can't calculate throughput: division by zero")

for station in stations_list:
    print("station.Id:{}, station.total_pkt_time:{}".format(
        station.Id, station.total_pkt_time))

# for i in range(len(channel.start)):
#     x = [channel.start[i], channel.end[i]]
#     print(x)
#     y = [channel.operator[i], channel.operator[i]]
#     print(y)1

'''
draw loss figure
'''

for i in range(len(stations_list)):
    station = stations_list[i]
    loss = station.model.lossHitory
    print(len(loss))

    host = host_subplot(111)  # row=1 col=1 first pic
    # ajust the right boundary of the plot window
    plt.subplots_adjust(right=0.8)
    par1 = host.twinx()   

    # set labels
    host.set_xlabel("steps")
    host.set_ylabel("loss")
    # par1.set_ylabel("test-accuracy")

    # plot curves
    # grid = range(min(len(loss), len(loss_2), len(loss_3)))
    p1, = host.plot(range(len(loss)), loss, label="loss")
    # p2, = host.plot(range(len(loss_2)), loss_2, label="loss 2")

    # set location of the legend,
    # 1->rightup corner, 2->leftup corner, 3->leftdown corner
    # 4->rightdown corner, 5->rightmid ...
    host.legend(loc=5)

    # set label color
    host.axis["left"].label.set_color(p1.get_color())
    # host.axis["left"].label.set_color(p2.get_color())
    # host.axis["left"].label.set_color(p3.get_color())
    # par1.axis["right"].label.set_color(p2.get_color())

    # set the range of x axis of host and y axis of par1
    # host.set_xlim([-200, 5200])
    # par1.set_ylim([-0.1, 1.1])

    plt.draw()
    # plt.show()
    plt.savefig('./fig/Epoch_{}_station_{}.jpg'.format(cfg.NUM_EPOCHS, i))
    plt.close()

# for station in stations_list:
#     print(len(station.model.lossHitory))
