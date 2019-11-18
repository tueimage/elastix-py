#!/usr/bin/env python
#
# Scroll through a 3D image using a Slicer object.
# 
# Minimal working example:
# import numpy as np
# import matplotlib.pyplot as plt
# image = np.ones((10, 10, 10))
# for i in range(len(image)):
#     image[i, i, i] = 0
# fig, ax = plt.subplots()
# Slicer(image).plot(ax)
# plt.show()

import time


class Slicer:
    
    def __init__(self, volume, default_index=0, scrolling=True, keyboard=True):
        self.volume = volume
        self.index = default_index
        self.scrolling = scrolling
        self.keyboard = keyboard
    
    def plot(self, ax, *args, **kwargs):
        
        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.get_figure()
        
        self.ax = ax
        self.figure = fig
        
        ax.index = self.index if self.index < self.volume.shape[0] else self.volume.shape[0] - 1

        ax.volume = self.volume.astype('float32')        
        ax.set_title('{}/{}'.format(ax.index, ax.volume.shape[0] - 1))
        ax.imshow(ax.volume[ax.index], *args, **kwargs)
        
        try:
            if fig.connections:
                pass
        except AttributeError:
            fig.canvas.mpl_connect('scroll_event', lambda x: self._process_scroll(x))
            fig.connections = True

    def set_slice(self, index):
        ax = self.ax
        try:
            ax.images[0].set_array(ax.volume[index])
            ax.index = index
            ax.set_title('{}/{}'.format(ax.index, ax.volume.shape[0] - 1))
        except AttributeError and IndexError:
            pass
        self.figure.canvas.draw()
        self.figure.canvas.draw()

    def _process_scroll(self, event):
        fig = event.canvas.figure
        if event.button == 'up':
            if event.inaxes:
                _previous_slice([event.inaxes])
            fig.canvas.draw()
        elif event.button == 'down':
            l = []
            if event.inaxes:
                _next_slice([event.inaxes])
            fig.canvas.draw()


def _previous_slice(axes):
    max_axes = _get_max_slice(axes)
    ax = axes[0]
    try:
        volume = ax.volume
        ax.index = (ax.index - 1) if ax.index > 1 else 0
        ax.images[0].set_array(volume[ax.index])
        ax.set_title('{}/{}'.format(ax.index, ax.volume.shape[0] - 1))
    except AttributeError:
        pass

def _next_slice(axes):
    ax = axes[0]
    try:
        if ax.index <= ax.volume.shape[0] - 1:
            if ax.index < ax.volume.shape[0] - 1:
                ax.index += 1
                ax.images[0].set_array(ax.volume[ax.index])
                ax.set_title('{}/{}'.format(ax.index, ax.volume.shape[0] - 1))
    except AttributeError:
        pass

def _get_max_slice(axes):
    m = 0
    for ax in axes:
        try:
            if ax.index > m:
                m = ax.index
        except AttributeError:
            pass
    l = []
    for ax in axes:
        try:
            if ax.index == m:
                l.append(ax)
        except AttributeError:
            pass
    return l


if __name__ == '__main__':
    
    import numpy as np
    import matplotlib.pyplot as plt
    import SimpleITK as sitk

    # Make an example image
    # image = np.ones((10, 10, 10))
    # for i in range(len(image)):
    #     image[i, i, i] = 0

    image = sitk.GetArrayFromImage(sitk.ReadImage('/Users/Koen/repos/essential-skills/example_data/chest_ct.mhd'))

    # Make an matplotlib axis object
    fig, ax = plt.subplots()

    # Make a slicer object and plot it on the axis object
    Slicer(image).plot(ax, cmap='gray')
    ax.set_axis_off()
    plt.show()
