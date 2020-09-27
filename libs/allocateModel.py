import copy
import random
import torch


class Allocator:
    def __init__(self, stations_list, modelSavePath):
        self.stations_list = stations_list
        self.nStation = len(stations_list)
        self.bestStationId = -1
        self.bestModel = None
        self.bestTargetModel = None
        self.allocateDestinatonId = -1
        self.modelSavePath = modelSavePath

        # seem useless
        # self.loadBestModel()

    def allocateModel(self):
        stations_list = self.stations_list
        # find best model
        max_total_pkt_time = -1
        max_total_pkt_time_stationIndex = -1
        tmp_best_stationId = -1
        for i in range(len(stations_list)):
            stationRL = stations_list[i]
            if stationRL.model.decisionCount < stationRL.model.maxRandomDecisionCount:
                return
            if stationRL.total_pkt_time > max_total_pkt_time:
                max_total_pkt_time = stationRL.total_pkt_time
                max_total_pkt_time_stationIndex = i
                tmp_best_stationId = stationRL.Id

        if tmp_best_stationId == self.bestStationId:
            print("best station not change")
            return

        self.bestStationId = tmp_best_stationId

        print("max_total_pkt_time: ", max_total_pkt_time)

        #  and self.allocateDestinatonId != -1:
        if max_total_pkt_time == 0:
            return

        # save best model to memory
        self.bestModel = copy.deepcopy(
            stations_list[max_total_pkt_time_stationIndex].model.model.
            state_dict())
        self.bestTargetModel = copy.deepcopy(
            stations_list[max_total_pkt_time_stationIndex].model.target_model.
            state_dict())

        # withdraw bestModel from last allocateDestinatonId
        if self.allocateDestinatonId:
            for station in stations_list:
                if station.Id != self.allocateDestinatonId:
                    continue
                random_index = max_total_pkt_time_stationIndex
                while (random_index in [
                        stations_list.index(station),
                        max_total_pkt_time_stationIndex
                ]):
                    random_index = random.randint(0, self.nStation - 1)
                print(
                    "random_index:{}, stations_list.index(station):{}".format(
                        random_index, stations_list.index(station)))
                self.copyModelWeight(random_index,
                                     stations_list.index(station))

        # allocate a random model to staion[ stationIndex ]
        random_index = max_total_pkt_time_stationIndex
        while (random_index == max_total_pkt_time_stationIndex):
            random_index = random.randint(0, self.nStation - 1)
        print("random_index:{}, max_total_pkt_time_stationIndex:{}".format(
            random_index, max_total_pkt_time_stationIndex))

        self.copyModelWeight(random_index, max_total_pkt_time_stationIndex)

        # allocate best model to a random station
        random_index = max_total_pkt_time_stationIndex
        while (random_index == max_total_pkt_time_stationIndex):
            random_index = random.randint(0, self.nStation - 1)

        self.allocateBestWeight(random_index)
        self.allocateDestinatonId = stations_list[random_index].Id

    def copyModelWeight(self, modelOrgin, modelDes):
        stations_list = self.stations_list
        stations_list[modelDes].model.model.load_state_dict(
            stations_list[modelOrgin].model.model.state_dict())
        stations_list[modelDes].model.target_model.load_state_dict(
            stations_list[modelOrgin].model.target_model.state_dict())

    def allocateBestWeight(self, modelDes):
        stations_list = self.stations_list
        stations_list[modelDes].model.model.load_state_dict(self.bestModel)
        stations_list[modelDes].model.target_model.load_state_dict(
            self.bestTargetModel)

    def saveBestModel(self):
        print("==> saving best model...")
        savePath = self.modelSavePath + "StationRl_Best.tar"
        torch.save(
            {
                "model_state_dict": self.bestModel,
                "target_model_state_dict": self.bestTargetModel
            }, savePath)

    def loadBestModel(self):
        print("==> loading best model...")
        savePath = self.modelSavePath + "StationRl_Best.tar"
        try:
            checkpoint = torch.load(savePath)
            self.bestModel = checkpoint["model_state_dict"]
            self.bestTargetModel = checkpoint["target_model_state_dict"]
        except:
            print("[Error] can't load best model")
