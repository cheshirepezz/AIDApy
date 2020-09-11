"""This module implements a multilayer perceptron

Author: Jannis Teunissen"""

import torch.nn as nn


class RegressorMlp(nn.Module):
    """Class to construct fully connected neural networks with a
    number of hidden layers"""

    def __init__(self, layer_sizes, afunc=nn.ReLU):
        """Initialize a multilayer perceptron

        :param layer_sizes: list of layer sizes
        :param afunc: activation function

        """
        super().__init__()

        n_layers = len(layer_sizes)
        self.net = nn.Sequential()

        for i in range(n_layers - 1):
            self.net.add_module('layer_{}'.format(i),
                                nn.Linear(layer_sizes[i], layer_sizes[i+1]))
            # Add activation function, except for the last layer
            if afunc and i != n_layers - 2:
                self.net.add_module('afunc_{}'.format(i), afunc())

        self.net.double()       # We use doubles by default

    def forward(self, X, **kwargs):
        return self.net(X)
