#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 09:03:03 2018

Using
Animals with Attributes Dataset, http://attributes.kyb.tuebingen.mpg.de
(C) 2009 Christoph Lampert <chl@tuebingen.mpg.de>

@author: dominik
"""


import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
import collect_data as cd

inputSVM_pattern =  './results/%s-SVM.pic.bz2'
inputLogReg_pattern =  './results/%s-LogReg-C=%s.pic.bz2'
inputLogReg_pattern_simple =  './results/%s-LogReg.pic.bz2'
inputLogRegCV_pattern =  './results/%s-LogRegCV.pic.bz2'

def testAllLogRegAccuracy(C):
    scores = []
    data, labels = cd.collectHistograms(cd.test_classes)
    labels = 2 * labels -1
    for i in range(85):
        scores.append(testClassifier(data, labels[:,i], i, inputLogReg_pattern % (cd.attributenames[i], str(C))))
    return np.array(scores)

def testAllLogRegCVAccuracy():
    scores = []
    data, labels = cd.collectHistograms(cd.test_classes)
    labels = 2 * labels -1
    for i in range(85):
        scores.append(testClassifier(data, labels[:,i], i, inputLogRegCV_pattern % cd.attributenames[i]))
    return np.array(scores)

def testLogRegAccuracy(attributeId, C):
    dataSet, labels = cd.createData(cd.test_classes, attributeId)
    data = cd.flattenDataSet(dataSet)
    filename = inputLogReg_pattern % (cd.attributenames[attributeId], str(C))

    return testClassifier(data, labels, attributeId, filename)

def testClassifier(data, labels, attributeId, filename):
    classifier = cd.bzUnpickle(filename)
    score = classifier.score(data, labels)
    print('Score for attribute {0}:\n{1}'.format(cd.attributenames[attributeId], score))
    return score

def testLogRegCVAccuracy(attributeId):
    dataSet, labels = cd.createData(cd.test_classes, attributeId)
    data = cd.flattenDataSet(dataSet)
    filename = inputLogRegCV_pattern % cd.attributenames[attributeId]

    return testClassifier(data, labels, attributeId, filename)

def scoreClassifiers(classes, input_pattern):
    attributeMatrix = (cd.attribute_matrix + 1.) / 2.
    attributesProb = np.sum(attributeMatrix, axis=0) / 50
    classProb = np.prod(np.abs(1 - attributesProb[np.newaxis,:] - attributeMatrix), axis=1)
    classProb = np.array([classProb[i] for i in range(50) if cd.classnames[i] in classes])
    attributeMatrix = np.array([attributeMatrix[i,:] for i in range(50) if cd.classnames[i] in classes]).astype(np.int)

    data, labels = cd.collectHistograms(classes)
    classifiersProb = []
    for attributeId in range(85):
        filename = input_pattern % cd.attributenames[attributeId]
        classifier = cd.bzUnpickle(filename)
        classifiersProb.append(classifier.predict_proba(data))
    
    classifiersProb = np.array(classifiersProb)
    err = 0
    predicted = []

    for testSample in range(data.shape[0]):
        predictedClass = np.argmax(np.prod(classifiersProb[ :,np.newaxis, testSample, 0] *(1-attributeMatrix.T) + classifiersProb[ :, np.newaxis,testSample, 1] * attributeMatrix.T, axis=0) / classProb)

        predicted.append(predictedClass)
        if np.any(attributeMatrix[predictedClass,:] != labels[testSample,:]):
            err += 1
    err /= data.shape[0]
    print('Total average score: ', 1. - err)
    predicted = np.array(predicted)
    return predicted, createConfusionMatrix(predicted, labels, attributeMatrix)

def createConfusionMatrix(predicted, labels, attributeMatrix):
    def whichClass(attributes):
        return [i for i in range(attributeMatrix.shape[0]) if np.all(attributeMatrix[i,:] == attributes)][0]

    confMatrix = np.zeros((attributeMatrix.shape[0], attributeMatrix.shape[0]))
    for i in range(len(predicted)):
        confMatrix[whichClass(attributeMatrix[predicted[i]]), whichClass(labels[i,:])] += 1
    return confMatrix