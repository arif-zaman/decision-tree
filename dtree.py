import math
import random


# Input From CSV File
def fileInput():
    with open("data.csv",'r+') as fin:
        dataSet = [line.strip() for line in fin.readlines()]

    return dataSet


# Find Most Frequent Value In The Target Attribute
def mostFrequentValue(data, tAttr):
    # Get the Value of a Specific Column/Attribute
    matrix = [line[tAttr] for line in data]
    num = 0
    highest= None

    for value in unique(matrix):
        if matrix.count(value) > num:
            highest= value
            num = matrix.count(value)

    return highest


# Find The Set of Unique Values In The Target Attribute/Specific Column
def unique(tAttrValues):
    uniqueSet = set([])

    for item in tAttrValues:
        uniqueSet.add(item)

    return list(uniqueSet)


# Find The Set of Unique Values From The Attributes matrix
def getUniqueValues(data, attr_list):
    return unique([line[attr_list] for line in data])


# Find The Best Attribute - Fitness Function => ID3
def findBestAttribute(data, attr_list, tAttr, infoGainFunc):
    maxGain = 0.0
    bestAttr = None

    for attr in attr_list:
        calculateGain = infoGainFunc(data, attr, tAttr)
        if (calculateGain >= maxGain and attr != tAttr):
            maxGain = calculateGain
            bestAttr = attr

    return bestAttr


# Find Only Relevent Values For This Expansion
def getReleventValues(data, attr_list, value):
    data = data[:]
    relevent = []

    if not data:
        return relevent
    else:
        line = data.pop()
        if line[attr_list] == value:
            relevent.append(line)
            relevent.extend(getReleventValues(data, attr_list, value))
            return relevent
        else:
            relevent.extend(getReleventValues(data, attr_list, value))
            return relevent


# Calculate Entropy => ID3
def calculateEntropy(data, tAttr):
    frequency = {}
    entropy = 0.0

    # Calculate Class Types
    for line in data:
        if (frequency.has_key(line[tAttr])):
            frequency[line[tAttr]] += 1.0
        else:
            frequency[line[tAttr]] = 1.0

    # Calculate the Entropy for Each Class and Return Sum
    for freq in frequency.values():
        entropy += (-freq/len(data)) * math.log(freq/len(data), 2)

    return entropy



# Calculate Information Gain => ID3
def calculateGain(data, attr_list, tAttr):
    frequency = {}
    subsetEntropy = 0.0

    for line in data:
        if (frequency.has_key(line[attr_list])):
            frequency[line[attr_list]] += 1.0
        else:
            frequency[line[attr_list]] = 1.0

    for value in frequency.keys():
        p = frequency[value] / sum(frequency.values()) # p - Probablity
        subset = [line for line in data if line[attr_list] == value]
        subsetEntropy += p * calculateEntropy(subset, tAttr)

    return (calculateEntropy(data, tAttr) - subsetEntropy)


# Build Decision Tree Using ID3 Heuristic
def dTree(data, attr_list, tAttr, infoGainFunc):
    values = [line[tAttr] for line in data]
    default = mostFrequentValue(data, tAttr)

    if not data or (len(attr_list) - 1) <= 0:
        return default

    # If All The dataSet In The Dataset Have The Same Class Return That Class.
    elif values.count(values[0]) == len(values):
        return values[0]

    else:
        # Choose Next Best
        best = findBestAttribute(data, attr_list, tAttr,infoGainFunc)
        # Solve Recursively - Declare Emplty Dictionary
        tree = {best:{}}

        for value in getUniqueValues(data, best):
            # p - Parameter
            p1 = getReleventValues(data, best, value)
            p2 = [attr_list for attr_list in attr_list if attr_list != best]
            p3 = tAttr

            subtree = dTree(p1,p2,p3,infoGainFunc)
            tree[best][value] = subtree

    return tree


# Return Class For Specific Data
def returnClass(line, tree):
    # Node == String => Leaf Node
    # Return It As Answer
    if type(tree) == type("string"):
        return tree
    else:
        attr_list = tree.keys()[0]
        t = tree[attr_list][line[attr_list]]
        return returnClass(line, t)


# Find Class For Test Data
def classFinder(tree, data):
    classList = []

    for line in data:
        classList.append(returnClass(line, tree))

    return classList


# findResult The Program
def findResult(dataSet):
    attr_list = [attr_list.strip() for attr_list in dataSet.pop(0).split(",")]
    tAttr = attr_list[-1]

    random.shuffle(dataSet)
    num = int (.8*len(dataSet))
    trainData = dataSet[:num] # 80%
    testData = dataSet[num:] # 20%

    # train Data
    data = []
    for line in trainData:
        #print
        list1 = attr_list
        list2 = [value for value in line.split(",")]
        data.append( dict( zip(list1,list2) ) )

    tree = dTree(data, attr_list, tAttr, calculateGain)

    # test Data
    data = []
    for line in testData:
        data.append( dict( zip(attr_list,[value.strip() for value in line.split(",")]) ) )

    classList = classFinder(tree, data)

    tp,fp,tn,fn = 0,0,0,0
    for i in xrange(len(classList)):
        if classList[i] == testData[i][-1]:
            if classList[i] == "0":
                tn += 1
            else:
                tp += 1
        else:
            if classList[i] == "0":
                fn += 1
            else:
                fp += 1

    return tp,fp,tn,fn


# Offline Tasks
def statistics(n):
    dataset = fileInput()
    Accuracy, Precision, Recall, F_measure, G_mean = [], [], [], [], []

    x = -1
    print "Please wait ....."
    print "Performance Measure - Over %d Run :" % n
    for i in xrange(n):
        data = dataset[:]

        try:
            #t = true , f = false , p = positive , n = negetive
            tp,fp,tn,fn = findResult(data)
            x += 1

            temp = float((tp+tn))/(tp+fp+tn+fn)
            Accuracy.append(temp)
            temp = float(tp)/(tp+fp)
            Precision.append(temp)
            temp = float(tp)/(tp+fn)
            Recall.append(temp)

            temp = 2*(Recall[x]*Precision[x])/float((Recall[x]+Precision[x]))
            F_measure.append(temp)

            temp1 = float(tp)/(tp+fn)
            temp2 = float(tn)/(tn+fp)

            temp = math.sqrt(temp1*temp2)
            G_mean.append(temp)

        except:
            continue

    if Accuracy:
        print
        print "Accuracy :"
        print ("\tMaximum : %4.2f \n\tMinimum : %4.2f") % (max(Accuracy) * 100, min(Accuracy) * 100)
        print
        print "Precision :"
        print ("\tMaximum : %4.2f \n\tMinimum : %4.2f") % (max(Precision) * 100, min(Precision) * 100)
        print
        print "Recall :"
        print ("\tMaximum : %4.2f \n\tMinimum : %4.2f") % (max(Recall) * 100, min(Recall) * 100)
        print

        print
        print " Average : "
        print ("\t Accuracy : %4.2f") % ((sum(Accuracy)/len(Accuracy)) * 100)
        print ("\t Precision : %4.2f") % ((sum(Precision)/len(Precision)) * 100)
        print ("\t Recall : %4.2f") % ((sum(Recall)/len(Recall)) * 100)
        print ("\t F_measure : %4.2f") % ((sum(F_measure)/len(F_measure)) * 100)
        print ("\t G_mean : %4.2f") % ((sum(G_mean)/len(G_mean)) * 100)
        print
    else:
        print "Error !!!"

    print x+1


if __name__ == "__main__":
   statistics(50)
