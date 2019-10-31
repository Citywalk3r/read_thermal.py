#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import glob
import argparse
import io
import json
import os
import re
import csv
from PIL import Image
from math import sqrt, exp, log
from matplotlib import cm
from matplotlib import pyplot as plt
import numpy as np
# from pysal.weights.Distance import DistanceBand


class LeafRecognitionBaseline:

    def __init__(self, is_debug=False):
        self.is_debug = is_debug
        self.cropped_rgb_img_filename = ""
        self.thermal_img_filename = ""

        self.rgb_image_np = None
        self.thermal_image_np = None

        self.cropped_img_suffix = '_rgb_image_cropped.jpg'
        self.thermal_img_suffix = '_thermal.png'
    pass

    def process_images(self, directory):
        if self.is_debug:
            print("INFO Image directory:{}".format(directory))

        image_name_without_suffix = directory.split("\\")[3]
        self.cropped_rgb_img_filename = directory + '\\' + image_name_without_suffix + self.cropped_img_suffix
        self.thermal_img_filename = directory + '\\' + image_name_without_suffix + self.thermal_img_suffix

        if not os.path.isfile(self.cropped_rgb_img_filename):
            raise ValueError("Input rgb image does not exist or this user don't have permission on this file")

        if not os.path.isfile(self.thermal_img_filename):
            raise ValueError("Input thermal image does not exist or this user don't have permission on this file")

        self.rgb_image_np = self.get_image_np(self.cropped_rgb_img_filename)
        self.thermal_image_np = self.get_image_np(self.thermal_img_filename)

        # Removing the alpha channel of the png thermal image
        self.thermal_image_np = self.thermal_image_np[:, :, :-1]

    def calculate_vegetation_index(self):

        vegetation_index = np.empty((self.rgb_image_np.shape[0], self.rgb_image_np.shape[1]), dtype='uint16')

        for i in range(self.rgb_image_np.shape[0]):
            for j in range(self.rgb_image_np.shape[1]):
                R = int(self.rgb_image_np[i, j, 0])
                G = int(self.rgb_image_np[i, j, 1])
                B = int(self.rgb_image_np[i, j, 2])

                if G+B == 0:
                    vegetation_index[i][j] = 0
                elif G-R < 0:
                    vegetation_index[i][j] = 1
                else:
                    vegetation_index[i][j] = (G-R)/(G+B)

        result = self.rgb_image_np.copy()
        result[vegetation_index == 1] = (0, 0, 0)

        # plt.subplot(1, 2, 1)
        # plt.imshow(vegetation_index, cmap=plt.cm.binary, vmin=0, vmax=1)
        # plt.subplot(1, 2, 2)
        # plt.imshow(result)
        # plt.show()

    def get_image_np(self, image_path):

        visual_img = Image.open(image_path)
        visual_np = np.array(visual_img)

        return visual_np

    def plot(self):
        """
        Plot the rgb + thermal image (easy to see the pixel values)
        :return:
        """
        rgb_np = self.rgb_image_np
        thermal_np = self.thermal_image_np

        plt.subplot(1, 2, 1)
        plt.imshow(thermal_np, cmap='hot')
        plt.subplot(1, 2, 2)
        plt.imshow(rgb_np)
        plt.show()


class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):

        if text.startswith('R|'):

            return text[2:].splitlines()  

        # this is the RawTextHelpFormatter._split_lines

        return argparse.HelpFormatter._split_lines(self, text, width)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract and visualize Flir Image data', formatter_class=SmartFormatter)
    # parser.add_argument('-act', '--actions', help='R|Perform all available actions except for plot() for all images.\nIncludes the generation of 4 images and a csv file.\n'
    #                     '1. Original thermal image (60x80)\n2. Original rgb image (640x480)\n3. Downscaled rgb image (60x80)\n4. Cropped rgb image (494x335)\n'
    #                     '5. Thermal data csv file generated by using the attached metadata',required=False,  action='store_true')
    parser.add_argument('-dir', '--directory', type=str, help='Input directory.', required=False)
    # parser.add_argument('-p', '--plot', help='Generate a plot using matplotlib', required=False, action='store_true')
    # parser.add_argument('-exif', '--exiftool', type=str, help='Custom path to exiftool', required=False,
    #                     default='exiftool')
    # parser.add_argument('-csv', '--extractcsv', help='Export the data per pixel encoded as csv file',
    #                     required=False, action='store_true')
    # parser.add_argument('-s', '--scale', help='Downscale the original image to match the thermal image\'s dimensions',
    #                     required=False, action='store_true')
    parser.add_argument('-d', '--debug', help='Set the debug flag', required=False,
                        action='store_true')
    args = parser.parse_args()
    
    if args.debug:
        print("DEBUG Recommended Python version: > 3.5")
        print("DEBUG Your system's Python version: "+str(sys.version_info[0])+"."+str(sys.version_info[1]))

    lrb = LeafRecognitionBaseline(is_debug=args.debug)
    lrb.process_images(args.directory)
    lrb.calculate_vegetation_index()

    # if args.actions:
    #     image_path_list = glob.glob("images/*-*-*/Camera_*/*/")
   
    #     for image_path in image_path_list:
    #         if args.debug:
    #             print ("-------------------------------------------------------")
    # else:
        # lrb.process_images(args.directory)
        # if args.plot:
        #     lrb.plot()
        # if args.scale:
        #     lrb.image_downscale()
        # if args.extractcsv:
        #     lrb.export_data_to_csv()
        # lrb.save_images()