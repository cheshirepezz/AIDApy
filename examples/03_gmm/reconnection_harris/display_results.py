import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


# Case setting
TIME_STEP = '020000'
COARSE_LEVEL = 4
X_SIZE = 768 // COARSE_LEVEL
Y_SIZE = 512 // COARSE_LEVEL
SPECIES = 0
ESTIMATOR = 'cst'
Lx = 30
Ly = 40

# Font setting
LABEL_SIZE = 16
TICK_SIZE = 14
CBAR_SIZE = 16
CBAR_TICK_SIZE = 14

VMIN = 0.1
VMAX = 1.0

# Load results
filename = 'gmm_output_' + str(SPECIES)+ '_{0}_{1}_{2}x{3}.h5'.format(TIME_STEP,
                                                                      ESTIMATOR,
                                                                      X_SIZE, Y_SIZE)
f = h5py.File(filename, 'r')

# Load magnetic field
B_PATH = os.path.join('data', 'field')
B_FILENAME = 'DoubleHarris-Fields_{}.h5'.format(TIME_STEP)
B_FINAL_PATH = os.path.join(B_PATH, B_FILENAME)
with h5py.File(B_FINAL_PATH, 'r') as f_:
    Bx_field = list(f_['Step#0']['Block']['Bx']['0'])[0]
    By_field = list(f_['Step#0']['Block']['By']['0'])[0]
    Bz_field = list(f_['Step#0']['Block']['Bz']['0'])[0]
    Bxy_field = (Bx_field, By_field)
B_x_nb, B_y_nb = Bx_field.T.shape
x_b = np.linspace(-0.5, X_SIZE, B_x_nb)
y_b = np.linspace(-0.5, Y_SIZE * 2, B_y_nb)
X_grid_b, Y_grid_b = np.meshgrid(x_b, y_b)


stream_points = np.array([[0.01, y] for y in np.arange(0, Y_SIZE * 2 // 4 - 20, 4)]   +   [[0.01, y] for y in np.arange(Y_SIZE * 2 // 4 + 20, Y_SIZE * 2 // 2, 4)]
                         + [[11.0, Y_SIZE * 2 // 4 + 2.0], [X_SIZE, Y_SIZE * 2 // 4 + 16], [X_SIZE, Y_SIZE * 2 // 4 + 4], [X_SIZE - 16, Y_SIZE * 2 // 4 + 4]])

for key in f.keys():
    data = np.array(f.get(key))
    data_to_plot = data.reshape((X_SIZE, Y_SIZE)).T
    fig = plt.figure()

    if key == '{}n_comp'.format(SPECIES):
        plt.imshow(data_to_plot, origin='lower',
                   cmap=cm.get_cmap('cubehelix_r', 5))
        cbar = plt.colorbar(ticks=range(1, 6), orientation='horizontal')
        plt.clim(0.5, 5.5)

    elif key == '{}energy_drop'.format(SPECIES):
        plt.imshow(data_to_plot, origin='lower', vmin=VMIN,
                   vmax=VMAX, cmap=cm.get_cmap('gnuplot2'))
        cbar = plt.colorbar(orientation='horizontal')

    elif key == '{}energy_deviation'.format(SPECIES):
        plt.imshow(data_to_plot, origin='lower', vmin=VMIN, vmax=VMAX,
                   cmap=cm.get_cmap('gnuplot2_r'))
        cbar = plt.colorbar(orientation='horizontal')

    elif key == '{}likelihood'.format(SPECIES):
        plt.imshow(data_to_plot, origin='lower', cmap=cm.get_cmap('gnuplot2'))
        cbar = plt.colorbar(orientation='horizontal')
    else:
        plt.imshow(data_to_plot, origin='lower', cmap=cm.get_cmap('gnuplot2'))
        cbar = plt.colorbar(orientation='horizontal')

    plt.xlabel('x', size=LABEL_SIZE, labelpad=-5)
    plt.ylabel('y', size=LABEL_SIZE)
    plt.xticks(np.arange(-0.5, X_SIZE + 0.5, X_SIZE // 3),
               np.arange(0, Lx + 1, Lx // 3))
    plt.yticks(np.arange(-0.5, Y_SIZE * 2 + 0.5, Y_SIZE * 2 // 8),
               np.arange(0, Ly + 1, Ly // 8))
    plt.xlim((-0.5, X_SIZE - 0.5))
    plt.ylim((-0.5 + (Y_SIZE * 2 // 2) / 4, Y_SIZE * 2 // 2 - 0.5 - (Y_SIZE * 2 // 2) / 4))

    ax = plt.gca()
    cbar.ax.tick_params(labelsize=CBAR_TICK_SIZE)
    ax.streamplot(X_grid_b, Y_grid_b, Bx_field, By_field, color='k',
                  linewidth=0.8, arrowstyle='-', density=35,
                  start_points=stream_points)
    # We change the fontsize of minor ticks label
    ax.tick_params(axis='both', which='major', labelsize=TICK_SIZE)
    plt.title(key)
    output_name = '{0}_{1}_{2}_{3}x{4}.pdf'.format(key, TIME_STEP, ESTIMATOR,
                                                   X_SIZE, Y_SIZE)
    if not os.path.exists('figures'):
        os.mkdir('figures')

    plt.savefig(os.path.join('figures', output_name))

plt.show()
