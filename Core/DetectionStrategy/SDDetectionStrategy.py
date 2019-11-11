# -*- coding: utf-8 -*-
# @Time    : 2019/10/19 20:08
# @Author  : 何盛信
# @Email   : 2958029539@qq.com
# @File    : SDDetectionStrategy.py
# @Project : RoadExtraction
# @Software: PyCharm

import numpy as np
from numpy import ndarray
from PyQt5.QtGui import QImage
from Core.DetectionAlgorithm.DetectionParameters import DetectionParameters
from Core.DetectionAlgorithm.SingleDirectionDetection import single_direction_detection
from DetectObjects.CircleSeed import CircleSeed, CircleSeedNp
from .AbstractDetectionStrategy import AbstractDetectionStrategy


class SDDetectionStrategy(AbstractDetectionStrategy):

    def __init__(self):
        super(SDDetectionStrategy, self).__init__()

    def road_detect(self, image: QImage, parent_seed: CircleSeed, detection_param: DetectionParameters, angle_interval):
        return single_direction_detection(image, parent_seed, detection_param, angle_interval)

    def analysis_peripheral_condition(self, candidate_seeds: list, detection_param: DetectionParameters):
        """
        候选种子的验证
        :param candidate_seeds: 待验证的候选种子
        :param detection_param: 校验常量参数
        :return: 返回通过验证的候选种子
        """
        temp_result = None
        for index, candidate_seed in enumerate(candidate_seeds):  # type: int, CircleSeedNp
            if candidate_seed.spectral_distance <= detection_param.SSD:
                if index == 0:
                    return [candidate_seed]
                if not temp_result:
                    temp_result = candidate_seed
                elif temp_result.spectral_distance > candidate_seed.spectral_distance:
                    temp_result = candidate_seed
        return [temp_result] if temp_result else []

    def road_detection(self, image, parent_seed, ref_seed, angle_interval, detection_strategy, detection_param):
        """
        根据父种子、检测策略和有效角度范围生成候选种子（未经筛选）。
        当不指定有效有效角度范围时，会沿着父种子的方向生成一个候选种子
        :param image: 源图片像素矩阵：rgb格式
        :type image: ndarray
        :param parent_seed: 用于生成候选种子的父种子
        :type parent_seed: CircleSeed
        :param ref_seed: 光谱信息参考种子
        :type ref_seed: CircleSeedNp
        :param angle_interval: 角度间距
        :type angle_interval: float
        :param detection_strategy: 道路跟踪检测的策略
        :type detection_strategy: DetectionStrategy
        :param detection_param: 道路跟踪检测的常数参数
        :type detection_param: DetectionParameters
        :return: 返回生成的候选种子列表
        :rtype: list
        """
        candidate_seeds = AbstractDetectionStrategy.generate_candidate_seeds(
            image, parent_seed, ref_seed, angle_interval, detection_strategy, detection_param)
        if candidate_seeds is None or len(candidate_seeds) <= 0:
            return []

        temp_result = None
        for index, candidate_seed in enumerate(candidate_seeds):  # type: int, CircleSeedNp
            if candidate_seed.spectral_distance <= detection_param.SSD:
                if index == 0:
                    return [candidate_seed]
                if not temp_result:
                    temp_result = candidate_seed
                elif temp_result.spectral_distance > candidate_seed.spectral_distance:
                    temp_result = candidate_seed
        return [temp_result] if temp_result else []

