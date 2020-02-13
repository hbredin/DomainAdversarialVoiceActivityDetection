#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2020 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Marvin Lavechin - marvinlavechin@gmail.com

from pyannote.audio.train.callback import Callback


class DomainLossScheduler(Callback):
    """
    Callback for implementing a scheduler for the domain loss.
    This class will make alpha, the weight associated to the domain loss,
    grow according to a linear or an exponential growth.

    The class expects :
        - start :     the epoch from which to start updating alpha
        - end :       the epoch from which to stop updating alpha
        - lower :     the initial value of alpha
        - higher :    the end value of alpha
        - growth :    must belong to ['linear', 'exponential']

    It will fit the value of alpha to :

        - f(n) = c1 * n + c2        if growth == 'linear'
        - f(n) = c1 * a ** n + c2   if growth == 'exponential'

    where :
    n is the current epoch.
    a is the exponential base, fixed at 1.03.
    c1 and c2 are computed such that the beginning and end constraints
    are respected, that means :
    - The value of alpha must be equal to lower before reaching epoch start.
    - The value of alpha must be equal to higher after eaching epoch end.

                            (alpha)
                                ^
                        higher  |           _______
                                |          /
                                |         /
                                |        /
                                |       /
                                |      /
                        lower   |_____/
                                ------------------> (nb_epochs)
                                    start   end

    Reference

    Use case
    --------
    Here's what expected in the config.yml :

    callbacks:
      - name: callbacks.scheduler_domain_loss.DomainLossSchedulerCallback
        params:
          start: 0
          end: 150
          lower: 0
          higher: 10
          growth: linear
    """

    def __init__(self, start, end, lower, higher, growth):
        """
        Initialize domain loss scheduler callback class.
        This will update the weight alpha associated to the domain loss
        during the training.

        Parameters
        ----------
        start :     the lower bound from which to start updating alpha
        end :       the higher bound from which to stop updating alpha
        lower :     the initial value of alpha
        higher :    the end value of alpha
        growth :    must belong to ['linear', 'exponential']
        """
        super().__init__()
        self.start = start
        self.end = end
        self.lower = lower
        self.higher = higher
        self.growth = growth
        self.base = 1.03    # base for the exponential growth

        if growth not in ['linear', 'exponential']:
            msg = (
                f'{growth} domain loss scheduler has not been implemented yet. '
                f'Please choose amongst [linear, exponential]'
            )
            raise NotImplementedError(msg)

        if self.lower > self.higher or self.start > self.end:
            msg = (
                f'Please check than lower < higher and start < end'
            )
            raise ValueError(msg)

        # Compute constants factors, so that the beginning,
        # and end constraints are respected
        if self.growth == "linear":
            self.c1 = (higher - lower) / (end - start)  # slope
            self.c2 = higher - end*self.c1              # intercept
        elif self.growth == "exponential":
            self.c1 = (higher - lower) / (self.base**end - self.base**lower)
            self.c2 = lower - self.c1*self.base**start

    def on_epoch_start(self, trainer):
        nb_epochs = trainer.epoch_

        if self.growth == "linear":
            trainer.alpha = self.c1 * nb_epochs + self.c2
        elif self.growth == "exponential":
            trainer.alpha = self.c1*self.base**nb_epochs + self.c2

        # Log value of alpha in tensorboard
        trainer.tensorboard_.add_scalar(
            f'train/alpha', trainer.alpha,
            global_step=trainer.epoch_)