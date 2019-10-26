# -*- coding: utf-8 -*-
# @Time    : 2019/10/3 20:42
# @Author  : 何盛信
# @Email   : 2958029539@qq.com
# @File    : Utils.py
# @Project : RoadExtraction
# @Software: PyCharm

from math import pow, sqrt
from PyQt5.QtCore import QPoint, QRectF
from PyQt5.QtGui import QColor, QImage, QPainterPath
from DetectObjects.Pixels import SeedPixel
from Core.Exception import RadiusOverBorder


class GrayPixelsSet:
    """灰色像素集"""
    # def __init__(self, gray_difference: int = 40, gray_min: int = 20, gray_max=200):
    #     self._gray_difference = gray_difference if 0 < gray_difference < 200 else 40
    #     self._gray_min = gray_min if 0 < gray_min < 100 and gray_min < gray_max else 20
    #     self._gray_max = gray_max if 50 < gray_max < 255 else 200

    gray_difference = 40
    standard_gay_min = 20
    standard_gray_max = 200

    @staticmethod
    def standard_gray(gray_min=20, gray_max=200) -> QColor:
        s_gray = int((gray_min + gray_max) / 2)
        return QColor(s_gray, s_gray, s_gray)

    @staticmethod
    def is_gray(color: QColor) -> bool:
        r = color.red()
        g = color.green()
        b = color.blue()
        return GrayPixelsSet.is_gray_of_rgb(r, g, b)

    @staticmethod
    def is_gray_of_rgb(r: int, g: int, b: int):
        res1 = GrayPixelsSet.standard_gay_min < r, g, b < GrayPixelsSet.standard_gray_max
        res2 = abs(r - g), abs(r - b), abs(g - b) <= GrayPixelsSet.gray_difference
        return all(res1) and all(res2)

    @staticmethod
    def get_gray_color_from(src_colors: [QColor]) -> [QColor]:
        return [color for color in src_colors if GrayPixelsSet.is_gray(color)]

    @staticmethod
    def get_gray_pixels_from(src_pixels: [SeedPixel]) -> [SeedPixel]:
        return [pixel for pixel in src_pixels if GrayPixelsSet.is_gray(pixel.color)]

    @staticmethod
    def get_similarity_gray_pixels(src_pixels: [SeedPixel], parent_reference_color: QColor, color_diff) -> []:
        """
        :param src_pixels:
        :param parent_reference_color:
        :param color_diff:
        :return:
        """

        def colour_distance1(rgb_1: QColor, rgb_2: QColor):
            R_1, G_1, B_1 = rgb_1.red(), rgb_1.green(), rgb_1.blue()
            R_2, G_2, B_2 = rgb_2.red(), rgb_2.green(), rgb_2.blue()
            rmean = (R_1 + R_2) / 2
            R = R_1 - R_2
            G = G_1 - G_2
            B = B_1 - B_2
            return sqrt((2 + rmean / 256) * (R ** 2) + 4 * (G ** 2) + (2 + (255 - rmean) / 256) * (B ** 2))

        def colour_distance2(rgb_1: QColor, rgb_2: QColor):
            R_1, G_1, B_1 = rgb_1.red(), rgb_1.green(), rgb_1.blue()
            R_2, G_2, B_2 = rgb_2.red(), rgb_2.green(), rgb_2.blue()
            return sqrt((R_1 - R_2)**2 + (G_1 - G_2)**2 + (B_1 - B_2)**2)

        result = []
        # 颜色相似度计算方法1
        if color_diff:
            result = [pixel for pixel in src_pixels if colour_distance2(pixel.color, parent_reference_color) <= color_diff]
        return result

        # 颜色相似度计算方法2
        # if color_diff:
        #     return [pixel for pixel in src_pixels if abs(pixel.r() - parent_reference_color.red()) < color_diff and abs(
        #         pixel.g() - parent_reference_color.green()) < color_diff and abs(
        #         pixel.b() - parent_reference_color.blue()) < color_diff]
        # else:
        #     return []


def get_pixels_from(image: QImage, position: QPoint, radius):
    """
    :param image: 源图片，该函数会根据所给的源图片、位置和半径获取这个范围内的像素集合
    :param position: 给定的圆的位置
    :param radius: 给定的半径
    :return:
    """

    if radius > min(image.width(), image.height()):
        raise RadiusOverBorder()

    result = list()
    for y in range(position.y() - radius, position.y() + radius + 1):
        for x in range(position.x() - radius, position.x() + radius + 1):
            if (pow(x - position.x(), 2) + pow(y - position.y(), 2)) <= pow(radius, 2):
                pixel_color = image.pixelColor(x, y)
                result.append(SeedPixel(QPoint(x, y), pixel_color))
    return result


def calculate_reference_color_of(circle_seed) -> QColor:
    seed_pixels = circle_seed.gray_pixels
    if not seed_pixels:
        return GrayPixelsSet.standard_gray()

    sum_r, sum_g, sum_b = 0, 0, 0
    for seed_pixel in seed_pixels:
        sum_r += seed_pixel.r()
        sum_g += seed_pixel.g()
        sum_b += seed_pixel.b()

    m = len(seed_pixels)
    return QColor(int(sum_r / m), int(sum_g / m), int(sum_b / m))


def is_accept_color_diff(color: QColor, color_diff):
    r, g, b = color.red(), color.green(), color.blue()
    res = abs(r - g), abs(r - b), abs(g - b) <= color_diff
    return all(res)


def get_circle_seed_path(circle_seed) -> QPainterPath:
    rect = QRectF(circle_seed.position.x() - circle_seed.radius, circle_seed.position.y() - circle_seed.radius,
                  circle_seed.radius * 2, circle_seed.radius * 2)
    seed_path = QPainterPath()
    seed_path.arcMoveTo(rect, 0)
    seed_path.arcTo(rect, 0, 360)
    seed_path.closeSubpath()
    return seed_path


def create_circle_path(x_center: int, y_center: int, radius: int) -> QPainterPath:
    rect = QRectF(x_center - radius, y_center - radius, radius * 2, radius * 2)
    circle_path = QPainterPath()
    circle_path.arcMoveTo(rect, 0)
    circle_path.arcTo(rect, 0, 360)
    circle_path.closeSubpath()
    return circle_path


def get_pixels_from_path(path: QPainterPath) -> list:
    polygons = path.toFillPolygons()
    result = []
    for polygon in polygons:
        for i in range(polygon.size()):
            result.append(polygon.at(i))
    return result


def combination22(src_list: [tuple, list]) -> list:
    result = []
    list_len = len(src_list)
    for i in range(0, list_len):
        for j in range(i + 1, list_len):
            result.append((src_list[i], src_list[j]))

    return result


if __name__ == '__main__':
    xc, yc = 500, 433
    radius = 20

    pixels = []
    for y in range(yc - radius, yc + radius + 1):
        for x in range(xc - radius, xc + radius + 1):
            if (pow(x - xc, 2) + pow(y - yc, 2)) <= pow(radius, 2):
                pixels.append([x, y])

    circle_path = create_circle_path(xc, yc, radius)
    path_pixels = get_pixels_from_path(circle_path)

    # print("原像素数： ", len(pixels))
    # print("path像素数： ", len(path_pixels))

    test_data = [1, 2, 3, 4, 5]
    combination_ = combination22(test_data)
    print(combination_)

    import time, random
    list2 = list(range(10000))
    list1 = list(range(10000000))
    test_num = random.randint(100, 1000000)

    ts = time.time()
    t = test_data in list1
    dt1 = time.time() - ts

    ts = time.time()
    t = test_data in list2
    dt2 = time.time() - ts

    print("dt1: ", dt1)
    print("dt2: ", dt2)
