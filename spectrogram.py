import matplotlib.pyplot as plt
import numpy as np
import internal_utility as iu
from ctypes import cast, c_void_p

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

def draw(results, mylib, half_h, c1):

    print ('drawing results...')
    plt.switch_backend('TkAgg')

    graphs = iu.from_ffi(results, mylib)  
    frequencies = graphs[4]
    detection = graphs[5]

    maxf = np.amax(frequencies)
    minf = np.amin([i for i in frequencies if i != 0])

    fig = plt.figure()
    add_subplot_zoom(fig)

    images = []
    for i in range(4):
        ax = fig.add_subplot(5,1,i+1)
        ax.imshow(np.transpose(graphs[i]), cmap='inferno', aspect='auto')
        ax.set_ylabel('Frequency(Hz)')
        ax.invert_yaxis()
        ax.set_xticks([])
        images.append(ax)

    images[0].set_title('Narrowband')
    images[1].set_title('Wideband')
    images[2].set_title('Combined')
    images[3].set_title('Harmonic Product Spectrum')

    scale = np.divide(graphs[1].shape[1], graphs[0].shape[1])
    lim = [int((minf - 10 if minf>10 else 0)/scale), int((maxf+10)/scale)]

    images[0].set_ylim(lim)
    images[1].set_ylim([minf - 10 if minf>10 else 0, maxf+10])
    images[2].set_ylim([minf - 10 if minf>10 else 0, maxf+10])
    images[3].set_ylim([minf - 10 if minf>10 else 0, maxf+10])

    changes = []
    for i in range(1, len(frequencies)):
        if abs(int(frequencies[i]) - int(frequencies[i-1])) > 5:
            changes.append(i-1)

    l1, = images[3].plot(frequencies, '-w', label='max')
    images[3].set_xlim(xmax=len(frequencies))
    for c in changes:
        images[3].axvline(x=c, color='green')
    images[3].legend(handles=[l1])

    ax1 = fig.add_subplot(5,1,5)
    ax1.set_yticks([])
    peaks = iu.peaks(detection, half_h, c1)

    repeats = iu.repeated_notes(peaks[0], changes, half_h, len(frequencies)/len(detection))

    l2, = ax1.plot(detection, '-co', label='onset detection', markevery=peaks[0])
    for tick in ax1.get_xticklabels():
        tick.set_rotation(90)

    for r in repeats:
        ax1.axvline(x=r)

    l3, = ax1.plot(peaks[1], '-r', label='dynamic threshold')
    ax1.set_xticks(peaks[0])
    ax1.legend(handles=[l2,l3])

    ax1.set_title('Onset Detection Function')
    ax1.set_xlim(xmin=0, xmax= len(detection))

    plt.subplots_adjust(0.04, 0.05, 0.97, 0.97, 0.13, 0.20)

    plt.get_current_fig_manager().window.state('zoomed')
    fig.canvas.set_window_title('Music Analysis')

    plt.show()

    mylib.clean2d.argtypes = [c_void_p]
    mylib.clean1d.argtypes = [c_void_p]

    for i,g in enumerate(iu.graphs.pointers):
        ptr = cast(g, c_void_p)
        mylib.clean2d(ptr) if i < 4 else mylib.clean1d(ptr)


