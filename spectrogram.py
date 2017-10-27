import matplotlib.pyplot as plt
import numpy as np
import internal_utility as iu
import sys
import time

def add_subplot_zoom(figure):

    zoomed_axes = [None]

    def on_click(event):
        ax = event.inaxes

        if ax is None:
            return

        if event.button != 3:
            return

        if zoomed_axes[0] is None:

            zoomed_axes[0] = (ax, ax.get_position())
            ax.set_position([0.04, 0.05, 0.93, 0.92])

            # hide all the other axes...
            for axis in event.canvas.figure.axes:
                if axis is not ax:
                    axis.set_visible(False)

        else:
            # restore the original state

            zoomed_axes[0][0].set_position(zoomed_axes[0][1])
            zoomed_axes[0] = None

            # make other axes visible again
            for axis in event.canvas.figure.axes:
                axis.set_visible(True)

        # redraw to make changes visible.
        event.canvas.draw()

    figure.canvas.mpl_connect('button_press_event', on_click)

def draw(file_name):

    print ('drawing...')
    plt.switch_backend('TkAgg')
    start_time = time.time()

    spectrogram_list = iu.analyze(sys.argv[1])
    
    '''
    variances, averages = [], []

    for fourier in spectrogram_list[0]:
        variances.append(np.var(fourier))
        averages.append(np.average(fourier))

    variances = iu.smooth(variances, 5)
    averages = iu.smooth(averages, 5)
    '''

    frequencies = [np.argmax(n) for n in spectrogram_list[3]]

    minf = np.amin(frequencies)
    maxf = np.amax(frequencies)

    fig = plt.figure()
    add_subplot_zoom(fig)

    images = []
    for i in range(4):
        ax = fig.add_subplot(4,1,i+1)
        ax.imshow(np.transpose(spectrogram_list[i]), cmap='inferno', aspect='auto')
        ax.set_ylabel('Frequency(Hz)')
        ax.invert_yaxis()
        images.append(ax)

    images[0].set_title('Narrowband')
    images[1].set_title('Wideband')
    images[2].set_title('Combined')
    images[3].set_title('Harmonic Product Spectrum')

    scale = np.divide(spectrogram_list[1].shape[1], spectrogram_list[0].shape[1])
    lim = [int((minf - 50 if minf>50 else 0)/scale), int((maxf+50)/scale)]

    images[0].set_ylim(lim)
    images[1].set_ylim([minf - 50 if minf>50 else 0, maxf+50])
    images[2].set_ylim([minf - 50 if minf>50 else 0, maxf+50])
    images[3].set_ylim([minf - 50 if minf>50 else 0, maxf+50])

    '''
    ax2 = images[0].twinx()
    l1, = ax2.plot(variances, '-c', label='variance')
    l2, = ax2.plot(averages, '-w', label='average')
    plt.legend(handles=[l1, l2])
    '''

    l4, = images[3].plot(frequencies, '-w', label='max')
    plt.legend(handles=[l4])

    plt.subplots_adjust(0.04, 0.05, 0.97, 0.97, 0.13, 0.25)

    print("Finished in %s seconds" % int(time.time() - start_time))

    plt.get_current_fig_manager().window.state('zoomed')
    fig.canvas.set_window_title('Music Analysis')
    
    plt.show()
