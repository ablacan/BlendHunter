# -*- coding: utf-8 -*-

""" DATA

This module defines classes and methods for preparing training data.

:Author: Samuel Farrens <samuel.farrens@cea.fr>

"""

import os
import numpy as np
import cv2
from .blend import Blender


class CreateTrainData(object):
    """ Create Training Data

    This class creates prepares training data for the BlendHunter class.

    Parameters
    ----------
    images : np.ndarray
        Stack of input images
    output_path : str
        Path to where the data will be saved
    train_fractions : tuple, optional
        Fraction of trainig, validation and testing samples from the input
        images, default is (0.45, 0.45, .1)
    classes : tuple, optional
        Names of the various data classes, default is ('blended',
        'not_blended')
    class_fractions : tuple, optional
        Fraction of samples to be allocated to each class, the default is
        (0.5, 0.5)

    Raises
    ------
    ValueError
        If train_fractions does not have 3 elements
    ValueError
        If the train_fractions elements do not sum to 1

    """

    def __init__(self, images, output_path, train_fractions=(0.45, 0.45, .1),
                 classes=('blended', 'not_blended'),
                 class_fractions=(0.5, 0.5), blend_images=True):

        self.images = np.random.permutation(images)
        self.path = output_path
        if len(train_fractions) != 3:
            raise ValueError('Fractions must be a tuple of length 3.')
        if sum(train_fractions) != 1:
            raise ValueError('Fractions must sum to 1.')
        self.train_fractions = train_fractions
        self.classes = classes
        self.class_fractions = class_fractions
        self.blend_images = blend_images
        self._image_num = 0

        self._make_output_dirs()

    def _make_output_dirs(self):
        """ Make Output Directories

        This method creates the directories where the samples will be stored.

        """

        bh_path = '{}/BlendHunterData'.format(self.path)
        train_path = '{}/train'.format(bh_path)
        valid_path = '{}/validation'.format(bh_path)

        if os.path.isdir(bh_path):
            raise FileExistsError('{} already exists. Please remove this '
                                  'directory or choose a new path.'
                                  ''.format(bh_path))

        os.mkdir(bh_path)
        os.mkdir(train_path)
        os.mkdir(valid_path)

        self._train_paths = ['{}/{}'.format(train_path, _class)
                             for _class in self.classes]
        self._valid_paths = ['{}/{}'.format(valid_path, _class)
                             for _class in self.classes]

        for _t_path, _v_path in zip(self._train_paths, self._valid_paths):
            os.mkdir(_t_path)
            os.mkdir(_v_path)

        if self.train_fractions[-1] > 0:
            self._test_path = '{}/test/test'.format(bh_path)
            os.mkdir('{}/test'.format(bh_path))
            os.mkdir(self._test_path)

    @staticmethod
    def _get_slices(array, fractions):
        """ Get Slices

        This method converts sample fractions into slice elemets for a given
        array.

        Parameters
        ----------
        array : np.ndarray
            Input array
        fractions : tuple
            Sample fractions

        Returns
        -------
        list
            Slice elements

        """

        frac_int = np.around(np.array(fractions) * array.shape[0]).astype(int)

        return [np.sum(frac_int[:_i]) for _i in range(1, frac_int.size + 1)]

    @classmethod
    def _split_array(cls, array, fractions):
        """ Split Array

        Split input array by the sample fractions.

        Parameters
        ----------
        array : np.ndarray
            Input array
        fractions : tuple
            Sample fractions

        Returns
        -------
        list
            List of sub-arrays

        """

        n_frac = len(fractions)
        split = np.split(array, cls._get_slices(array, fractions))

        return [split[_i] if _i < n_frac - 1 else np.vstack(split[_i:])
                for _i in range(n_frac)]

    @staticmethod
    def _rescale(array):
        """ Rescale

        Rescale input image to RGB.

        Parameters
        ----------
        array : np.ndarray
            Input array

        Returns
        -------
        np.ndarray
            Rescaled array

        """

        return np.array(array * 255).astype(int)

    def _write_images(self, images, path):
        """ Write Images

        Write images to jpeg files.

        Parameters
        ----------
        images : np.ndarray
            Array of images
        path : str
            Path where images should be written

        """

        for image in images:

            if len(image.shape) == 2:
                image = image.reshape(*image.shape, 1)

            if np.max(image) <= 1:
                image = self._rescale(image)

            cv2.imwrite('{}/image_{}.jpg'.format(path, self._image_num), image)
            self._image_num += 1

    def _blend_data(self, data_set):
        """ Blend Data Set

        Blend the first sample of the data set and combine the other set
        without blending.

        Parameters
        ----------
        data_set : list
            List of data samples

        Returns
        -------
        list
            Blended data set

        """

        if len(data_set) == 2:

            data_set[0] = Blender(data_set[0], ratio=0.5).blend()
            data_set[1] = Blender(data_set[1], ratio=1.5,
                                  blended=False).blend()

        return data_set

    def generate(self):
        """ Generate

        Generate training data.

        """

        image_split = self._split_array(self.images, self.train_fractions)

        train_set = self._split_array(image_split[0], self.class_fractions)
        valid_set = self._split_array(image_split[1], self.class_fractions)

        if self.blend_images:
            train_set = self._blend_data(train_set)
            valid_set = self._blend_data(valid_set)

        for images, path in zip(train_set, self._train_paths):
            self._write_images(images, path)
        for images, path in zip(valid_set, self._valid_paths):
            self._write_images(images, path)

        if self.train_fractions[-1] > 0:
            self._write_images(image_split[2], self._test_path)
