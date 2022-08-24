import sys

from django.shortcuts import render
import os
import json
import random
from django.http import JsonResponse
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from shutil import copyfile

# Create your views here.


def index(request):
    return render(request, "index.html")


'''
def api1(request):
    if request.method == "POST":
        files = request.FILES.get("uploadfile")
        print(files.name)
        # 把文件保存到项目中一个叫做uploads的文件夹下面
        file_ = os.path.join(BASE_DIR,"static","uploads", files.name)
        f = open(file_, "wb")
        for item in files.chunks():
            f.write(item)
        f.close()
        return JsonResponse({'upload_path': '/static/uploads/'+files.name})
    # 如果不是post请求则跳转到首页
    return render(request, "index.html")
'''


def save(request):
    if request.method == 'POST':
        print(request.POST.get("originalExample"))
        filePath = os.path.join(BASE_DIR, "static", "deal", "setting.json")
        settingDict = {
            'originalExample': request.POST.get("originalExample"),
            'attackMethod': request.POST.get("attackMethod"),
            'targetModel': request.POST.get("targetModel"),
            'queryCount': request.POST.get("queryCount"),
            # '
            # L2Distance': request.POST.get("L2Distance"),
            'attackPattern': request.POST.get("attackPattern")
        }
        jsonFile = json.dumps(settingDict)
        with open(filePath, "w") as f:
            f.write(jsonFile)
        return JsonResponse({"message": "参数设置成功!"})
    return render(request, "index.html")


def result(request):
    if request.method == 'POST':
        # 解析setting.json并查找识别结果的位置
        filePath = os.path.join(BASE_DIR, "static", "deal", "setting.json")
        with open(filePath) as f:
            allTabs = json.load(f)
            originalExample = allTabs['originalExample']
            attackMethod = allTabs['attackMethod']
            targetModel = allTabs['targetModel']
            attackPattern = allTabs['attackPattern']
            queryCount = allTabs['queryCount']
            # L2Distance = allTabs['L2Distance']
        advResultPath = originalExample + '/' + attackMethod + '/' + targetModel + '/' + attackPattern + '/' + queryCount + '/'
        norResultPath = originalExample + '/' + targetModel + '/'
        return JsonResponse({"advPath": advResultPath, "norPath": norResultPath})
    return render(request, "index.html")


'''
def api2(request):
    if request.method == "POST":
        #处理逻辑
        print("hello")
        upload_path = request.POST.get('name')

        deal_path = upload_path.replace("uploads","deal")

        try:
            copyfile(BASE_DIR+upload_path, BASE_DIR+deal_path)
        except IOError as e:
            print("Unable to copy file. %s" % e)
            exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)
        # print(name)
        #输出到/static/deal
        return JsonResponse({'upload_path': upload_path,'deal_path':deal_path})
        #return render(request, "index.html", context={'upload_path': upload_path, 'deal_path': deal_path})
'''


def compare(request):
    if request.method == 'POST':
        # 解析setting.json文件并随机挑选一定数量的识别结果(正常样本和对抗样本图片)，返回它们的路径
        filePath = os.path.join(BASE_DIR, "static", "deal", "setting.json")
        with open(filePath) as f:
            allTabs = json.load(f)
            originalExample = allTabs['originalExample']
            attackMethod = allTabs['attackMethod']
            targetModel = allTabs['targetModel']
            attackPattern = allTabs['attackPattern']
            queryCount = allTabs['queryCount']
            # L2Distance = allTabs['L2Distance']
        advImagesPath = originalExample + '/' + attackMethod + '/' + targetModel + '/' + attackPattern + '/' + queryCount + '/'
        normalImagesPath = originalExample + '/' + targetModel + '/'
        indexes = random.sample(range(0, 100), int(request.POST.get("count")))
        indexes.sort()
        return JsonResponse({"normalImages": normalImagesPath, "adversarialImages": advImagesPath, "indexes": indexes})
    return render(request, "index.html")


def evaluate(request):
    if request.method == 'GET':
        # 解析setting.json文件并将查找到对应的csv文件,解析csv文件,整理并返回这些数据
        filePath = os.path.join(BASE_DIR, "static", "deal", "setting.json")
        with open(filePath) as f:
            allTabs = json.load(f)
            originalExample = allTabs["originalExample"]
            attackMethod = allTabs["attackMethod"]
            targetModel = allTabs["targetModel"]
            queryCount = allTabs["queryCount"]
            # L2Distance = allTabs["L2Distance"]
            attackPattern = allTabs["attackPattern"]
        resultPath = BASE_DIR + '\\static\\deal\\adversarial\\' + originalExample + '\\' + \
                     attackMethod + '\\' + targetModel + '\\' + attackPattern + '\\' + queryCount + '\\evaluate.csv'
        # 数据操作区域，将结果存储为字典形式返回
        data = pd.read_csv(resultPath)
        data = data.drop(len(data) - 1)

        results = np.array(data["Results"])
        # 对抗样本的模型访问量分布表
        '''
        result1 = {}
        queries1 = np.array(data["Number_of_Model_Queries"])
        intervals_1 = np.percentile(queries1, (0, 20, 40, 60, 80, 100))
        segments_1 = pd.cut(queries1, intervals_1, right=True)
        counts1 = pd.value_counts(segments_1, sort=False)
        result_temp1 = counts1.to_dict()
        add1 = 1
        for i in result_temp1.items():
            key = str(i[0])
            value = i[1]
            if add1 == 1:
                value += np.sum(queries1 == np.min(queries1))
                add1 += 1
            result1[key] = float(value)
        print(result1)
        '''
        if attackMethod == "AdvPatch":
            L0_Weight = np.array(data["L0_Weight"])
            realL0Weight = []
            maxL0Weight = 0
            minL0Weight = 1
            for index in range(0, len(results)):
                if int(results[index]) == 1:
                    maxL0Weight = max(L0_Weight[index], maxL0Weight)
                    minL0Weight = min(L0_Weight[index], minL0Weight)
                    realL0Weight.append(L0_Weight[index])
            weightDict = {}
            indexDict = {}
            internal = (maxL0Weight - minL0Weight) / 5
            for i in range(0, 5):
                key = [minL0Weight + i * internal, minL0Weight + (i + 1) * internal]
                weightDict[str(key)] = 0
                indexDict[i] = key
            for weight in realL0Weight:
                if weight < indexDict[0][1]:
                    weightDict[str(indexDict[0])] = weightDict[str(indexDict[0])] + 1
                elif weight < indexDict[1][1]:
                    weightDict[str(indexDict[1])] = weightDict[str(indexDict[1])] + 1
                elif weight < indexDict[2][1]:
                    weightDict[str(indexDict[2])] = weightDict[str(indexDict[2])] + 1
                elif weight < indexDict[3][1]:
                    weightDict[str(indexDict[3])] = weightDict[str(indexDict[3])] + 1
                elif weight <= indexDict[4][1]:
                    weightDict[str(indexDict[4])] = weightDict[str(indexDict[4])] + 1
            oldWeightDict = weightDict
            weightDict = {}
            for k, v in indexDict.items():
                newKey = "[" + str(round(v[0] * 100, 2)) + "%, " + str(round(v[1] * 100, 2)) + "%]"
                weightDict[newKey] = oldWeightDict[str(v)]
            result1 = weightDict
        else:
            queryCount = np.array(data["Query_Count"])
            realQuery = []
            maxQuery = 0
            for index in range(0, len(results)):
                if int(results[index]) == 1:
                    maxQuery = max(queryCount[index], maxQuery)
                    realQuery.append(queryCount[index])
            queryDict = {}
            indexDict = {}
            internal = maxQuery / 15
            for i in range(0, 5):
                begin = (i + 1) * i / 2
                key = [begin * internal, (begin + i + 1) * internal]
                queryDict[str(key)] = 0
                indexDict[i] = key
            for query in realQuery:
                if query < indexDict[0][1]:
                    queryDict[str(indexDict[0])] = queryDict[str(indexDict[0])] + 1
                elif query < indexDict[1][1]:
                    queryDict[str(indexDict[1])] = queryDict[str(indexDict[1])] + 1
                elif query < indexDict[2][1]:
                    queryDict[str(indexDict[2])] = queryDict[str(indexDict[2])] + 1
                elif query < indexDict[3][1]:
                    queryDict[str(indexDict[3])] = queryDict[str(indexDict[3])] + 1
                elif query <= indexDict[4][1]:
                    queryDict[str(indexDict[4])] = queryDict[str(indexDict[4])] + 1
            result1 = queryDict
        # 对抗样本的扰动量分表布
        '''
        result2 = {}
        queries2 = np.array(data["L2_Difference_Between_Images"])
        intervals_2 = np.percentile(queries2, (0, 20, 40, 60, 80, 100))
        segments_2 = pd.cut(queries2, intervals_2, right=True)
        counts2 = pd.value_counts(segments_2, sort=False)
        result_temp2 = counts2.to_dict()
        add2 = 1
        for i in result_temp2.items():
            key = str(i[0])
            value = i[1]
            if add2 == 1:
                value += np.sum(queries2 == np.min(queries2))
                add2 += 1
            result2[key] = float(value)
        print(result2)
        '''

        differences = np.array(data["L2_Difference"])
        maxDiff = np.max(differences)
        e = maxDiff / 10
        differences = np.divide(differences, e)
        realDifference = []
        maxDifference = 0
        minDifference = 1000
        for index in range(0, len(results)):
            if int(results[index]) == 1:
                maxDifference = max(differences[index], maxDifference)
                minDifference = min(differences[index], minDifference)
                realDifference.append(differences[index])
        differenceDict = {}
        indexDict = {}
        internal = (maxDifference - minDifference) / 5
        for i in range(0, 5):
            key = [round(minDifference + i * internal, 4), round(minDifference + (i + 1) * internal, 4)]
            differenceDict[str(key)] = 0
            indexDict[i] = key
        for difference in realDifference:
            if difference < indexDict[0][1]:
                differenceDict[str(indexDict[0])] = differenceDict[str(indexDict[0])] + 1
            elif difference < indexDict[1][1]:
                differenceDict[str(indexDict[1])] = differenceDict[str(indexDict[1])] + 1
            elif difference < indexDict[2][1]:
                differenceDict[str(indexDict[2])] = differenceDict[str(indexDict[2])] + 1
            elif difference < indexDict[3][1]:
                differenceDict[str(indexDict[3])] = differenceDict[str(indexDict[3])] + 1
            elif difference <= indexDict[4][1]:
                differenceDict[str(indexDict[4])] = differenceDict[str(indexDict[4])] + 1
        result2 = differenceDict

        # 样本的目标置信度对比表
        result3 = {}
        baseConfidence = np.array(data["Confidence_Before"])
        # confidenceAfterAttack = np.array(data.iloc[:, 3])
        confidenceAfterAttack = np.array(data["Confidence_After"])
        temp = zip(baseConfidence, confidenceAfterAttack)
        group_bf = []
        for i in temp:
            group_bf.append(i)
        gap_3 = len(group_bf) // 10
        start = 0
        record_before = []
        record_after = []
        labels = []
        for i in range(10):
            record_before.append(round(group_bf[start][0], 2))
            record_after.append(round(group_bf[start][1], 2))
            labels.append("样本" + str(start))
            start += gap_3
        result3 = {'b': record_before, 'a': record_after, 'l': labels}
        print(result3)

        # 对抗攻击综合性能表
        # stealthyness 隐秘性
        stealthyness = data['L2_Difference'].sum() / len(data)
        stealthyness_max = data['L2_Difference'].max()
        stealthyness_min = data['L2_Difference'].min()
        stealthyness_ratio = (stealthyness - stealthyness_min) / (stealthyness_max - stealthyness_min) * 50
        stealthyness_ratio = round((100 - stealthyness_ratio), 2)
        # timeliness 时效性 Number_of_Model_Queries
        if attackMethod == "AdvPatch":
            timeliness_ratio = 100
        else:
            timeliness = data['Query_Count'].sum() / len(data)
            timeliness_max = data['Query_Count'].max()
            timeliness_min = data['Query_Count'].min()
            timeliness_ratio = (timeliness - timeliness_min) / (timeliness_max - timeliness_min) * 100
            timeliness_ratio = round((100 - timeliness_ratio), 2)
        # attack_success_rate 攻击成功率
        attack_success_rate = round(data['Results'].sum() / len(data) * 100, 2)
        result4 = {"隐秘性": stealthyness_ratio, "时效性": timeliness_ratio, "攻击成功率": attack_success_rate}
        print(result4)
        # rst_1 = list([1, 2, 3, 4, 5, 6])
        # return JsonResponse(
        #     {"queryCount": rst_1, "L2Distance": rst_1, "confidence": rst_1, "performance": rst_1})
        return JsonResponse({"queryCount": result1, "L2Distance": result2, "confidence": result3, "performance": result4, "attackMethod": attackMethod})
    return render(request, "index.html")


def poison(request):
    if request.method == 'POST':
        dirPath = os.path.join(BASE_DIR, "static", "deal", "poison", request.POST.get("scene"), "normal")
        print(dirPath)
        filePaths = os.listdir(dirPath)
        indexes = random.sample(range(1, len(filePaths)), int(request.POST.get("count")))
        indexes.sort()
        return JsonResponse({"indexes": indexes})
    return render(request, "index.html")

