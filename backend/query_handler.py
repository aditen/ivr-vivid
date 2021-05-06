from typing import List

from data_classes import FilterCriteria
import pandas as pd
import numpy as np


class QueryHandler:
    def __init__(self):
        print("Initialized query handler")

    def get_shots_based_on_yolo_position_and_class(self, yolo, query_position, class_query):
        query_filter=yolo[yolo["class"]==class_query]
        b = query_position
        confidence_filter=query_filter[query_filter["confidence"]>=0.5]
        confidence_filter["distance_to_query"] = confidence_filter.apply(lambda row : np.linalg.norm((row['centerX'],
              row['centerY'])-b), axis = 1)
        position_filter= confidence_filter[confidence_filter["distance_to_query"]<0.1]["filename"]
        query_result_shotframes=list(set(map(lambda x: x[:-8], position_filter))) #unique frames that contain the class query
        positions= confidence_filter[confidence_filter["distance_to_query"]<0.1][['filename', 'centerX', 'centerY']]
        positions = positions.sort_values(by='filename')
        sorted_shotframes = positions['filename']
        X = positions['centerX'].to_numpy()
        Y = positions['centerY'].to_numpy()
        numberofshots_in_query = len(X)
        print(numberofshots_in_query)
        sorted_shotframes=list(map(lambda x: x[:-8], sorted_shotframes)) #unique frames that contain the class query
        return sorted_shotframes, numberofshots_in_query

    def get_shots_based_nasnet_class(self, nasnet, class_query):
        query_filter=nasnet[nasnet["class"]==class_query]
        confidence_filter=query_filter[query_filter["confidence"]>=0.5]["filename"]
        query_result_shotframes=list(set(map(lambda x: x[:-8], confidence_filter))) #unique frames that contain the class query
        sorted_shotframes=sorted(query_result_shotframes)
        numberofshots_in_query = len(sorted_shotframes)
        return sorted_shotframes, numberofshots_in_query

    def get_shots_based_ocr_text(self, ocr_data, text_query):
        sorted_shotframes=sorted(ocr_data[ocr_data['output'].str.contains(text_query)]["filename"])
        query_result_shotframes=list(map(lambda x: x[:-8], sorted_shotframes))
        numberofshots_in_query = len(query_result_shotframes)
        return query_result_shotframes, numberofshots_in_query


    def handle_query(self, filter_criteria: FilterCriteria) -> List[List[str]]:
        print(filter_criteria)
        #filter_criteria: FilterCriteria
        # 1: Laura filters the keyframes
        # 2: Baris does the SOM on the keyframes
        # 3: Adrian gets the response and displays it on the GUI
        #print(self)

        #FilterCriteria(locatedObjects=[], classNames=['stage'], gridWidth=8, text=''
        number_of_yolo_queries = len(filter_criteria.locatedObjects)
        number_of_nasnet_queries = len(filter_criteria.classNames)
        sorted_shotframes = list()

        if number_of_yolo_queries > 0:
            yolo = pd.read_csv('/home/jonaslaura/Documents/ivr-vivid-main/backend/features_data/yolo.csv', index_col="idx")

            # get filtercriterias from canvas
            yolo_class_query=filter_criteria.locatedObjects[0].className
            x_offset = filter_criteria.locatedObjects[0].xOffset
            y_offset = filter_criteria.locatedObjects[0].yOffset
            width = filter_criteria.locatedObjects[0].width
            height = filter_criteria.locatedObjects[0].height

            # parse position to float between 0 and 1.
            #to do: access information in isLargeScreen, if no, 640 -> 344px, and 360 -> 171
            x_position = (x_offset +(width/2))/640
            y_position = (y_offset +(height/2))/360
            queryPosition = np.array((x_position, y_position))
            print(queryPosition)
            sorted_shotframes, numberofshots_in_query = self.get_shots_based_on_yolo_position_and_class(yolo, queryPosition, yolo_class_query)
            print("Yolo lenght" , numberofshots_in_query)

        if number_of_nasnet_queries > 0:
            nasnet = pd.read_csv('/home/jonaslaura/Documents/ivr-vivid-main/backend/features_data/nasnet_formated.csv')
            #get filter criterias Nasnet
            nasnet_class_query = filter_criteria.classNames[0]
            print("Nasnet query:", nasnet_class_query)
            sorted_shotframes_nasnet, numberofshots_in_query = self.get_shots_based_nasnet_class(nasnet, nasnet_class_query)
            print("Nasnet lenght" , numberofshots_in_query)
            if len(sorted_shotframes) > 0:
                sorted_shotframes = np.intersect1d(sorted_shotframes, sorted_shotframes_nasnet)
            else:
                sorted_shotframes = sorted_shotframes_nasnet

        if len(filter_criteria.text) > 0:
            #get filter criterias text (OCR)
            ocr_data = pd.read_csv('/home/jonaslaura/Documents/ivr-vivid-main/backend/features_data/combinedOCR.csv')
            ocr_data = ocr_data.dropna(subset=['output'])
            text_query = filter_criteria.text
            print("text query:", text_query)
            sorted_shotframes_text, numberofshots_in_query = self.get_shots_based_ocr_text(ocr_data, text_query)
            print("Final lenght" , numberofshots_in_query)
            if len(sorted_shotframes) > 0:
                sorted_shotframes = np.intersect1d(sorted_shotframes, sorted_shotframes_text)
            else:
                sorted_shotframes = sorted_shotframes_text

        print("Final lenght" , len(sorted_shotframes))
        # show selected keyframes
        all_kf_test=list(map(lambda x: 'https://iten.engineering/files/keyframes/'+ x[4:9]+"/"+x+"_RKF.png", sorted_shotframes))
        result_mat = []
        count = 0
        while count < len(all_kf_test):
            result_mat.append(all_kf_test[count:(count + filter_criteria.gridWidth)])
            count += filter_criteria.gridWidth
        return result_mat
