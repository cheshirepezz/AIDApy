"""
Example illustrating the use of the density estimation with Gaussian mxiture models
for a Double Harris sheet case.
The example data can be downloaded at: https://osf.io/sh89u/?view_only=4e4fd8f513a34ebebdcca1747a505581
See also AIDA paper: https://arxiv.org/abs/1910.10012
"""
import os
import sys
import h5py
import numpy as np
from mpi4py import MPI
from joblib import dump

from aidapy.ml.gmm import leggi_h5, clustering

# Initial parameters
species = 0
time_step = '020000'
estimator = 'cst'
case = 'new_reco'
COARSE_LEVEL = 4
file_input_first_part = 'data/particle/{}/'.format(time_step) + str(species) + 'subp'

gmm_dir_name = 'gmm_models'
aic_bic_dir_name = 'aic_bic'

if case == 'new_reco':
    XLEN = 24                   # Number of subdomains in the X direction
    YLEN = 16                   # Number of subdomains in the X direction
    ZLEN = 1                    # Number of subdomains in the X direction
    Lx = 30                     # Lx = simulation box length - x direction in m
    Ly = 20                     # Ly = simulation box length - y direction in m
    Lz = 0.1                    # Lz = simulation box length - z direction in m
    nxc = 768 // COARSE_LEVEL   # Size of the PIC mesh in x direction
    nyc = 512 // COARSE_LEVEL   # Size of the PIC mesh in y direction
    nzc = 1                      # Size of the PIC mesh in z direction
    nblockx = 1
    nblocky = 1
    nblockz = 1

file_output = 'gmm_output_' + str(species)+'_{0}_{1}_{2}x{3}.h5'.format(time_step, estimator, nxc, nyc)

# Compute the different values to run the script with MPI
if len(sys.argv) > 1:
    species = int(sys.argv[1])

# Parameters of the computational domain and initialize the matrices
dx = Lx / nxc
dy = Ly / nyc
dz = Lz / nzc
xrange_ = int(nxc / XLEN)
yrange = int(nyc / YLEN)
zrange = int(nzc / ZLEN)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
nxloc = int(xrange_ / nblockx)
nyloc = int(yrange / nblocky)
nzloc = int(zrange / nblockz)
kmeans_local = np.zeros((nxloc, nyloc, nzloc))

edrop_out = np.zeros((nxc, nyc, nzc))
tot_th_out = np.zeros((nxc, nyc, nzc))
edev_out = np.zeros((nxc, nyc, nzc))
tot_energy_out = np.zeros((nxc, nyc, nzc))
n_comp_out = np.zeros((nxc, nyc, nzc))
likelihood_out = np.zeros((nxc, nyc, nzc))
gmm_model_out = {}
aic_bic_out = {}


# Iterate over each sub-block
print('size', size)
icount = 0
for ivai in range(rank, XLEN*YLEN*ZLEN, size):
    iz = ivai // (XLEN * YLEN)
    itmp = (ivai % (XLEN * YLEN))
    iy = itmp // XLEN
    ix = itmp % XLEN
    print(rank, ivai, 'ix,iy,iz', ix, iy, iz)
    sys.stdout.flush()
    ibin = ix + iy * XLEN + iz * XLEN * YLEN
    file_input_full = file_input_first_part + str(ibin).zfill(6) + '.h5'

    if ibin >= 0 & ibin < XLEN * YLEN * ZLEN:
        qp, xp, yp, zp, up, vp, wp = leggi_h5(file_input_full)
        for ixloc in range(nxloc):
            for iyloc in range(nyloc):
                for izloc in range(nzloc):
                    isubx = ixloc * nblockx
                    isuby = iyloc * nblocky
                    isubz = izloc * nblockz
                    x0 = (ix * xrange_ + isubx) * dx
                    x1 = x0 + nblockx * dx
                    y0 = (iy * yrange + isuby) * dy
                    y1 = y0 + nblocky * dy
                    z0 = (iz * zrange + isubz) * dz
                    z1 = z0 + nblockz * dz
                    condition = (xp >= x0) & (xp < x1) & (yp >= y0) & (yp < y1)
                    X_gmm = np.transpose(np.array([np.extract(condition, up), \
                                     np.extract(condition, vp), \
                                     np.extract(condition, wp)]))
                    energy_drop, energy_dev, tot_energy, tot_thermal, n_components, gmm_model_, aic_bic_, likelihood_ = clustering(X_gmm, estimator=estimator)
                    isubxin = ixloc * nblockx
                    isubyin = iyloc * nblocky
                    isubzin = izloc * nblockz
                    edrop_out[ix * xrange_ + isubxin:ix * xrange_ + isubxin + nblockx, iy * yrange + isubyin:iy * yrange + isubyin+nblocky, iz * zrange + isubzin:iz * zrange + isubzin+nblockz] += energy_drop
                    tot_th_out[ix * xrange_ + isubxin:ix * xrange_ + isubxin + nblockx, iy * yrange + isubyin:iy * yrange + isubyin+nblocky, iz * zrange + isubzin:iz * zrange + isubzin+nblockz] += tot_thermal
                    edev_out[ix * xrange_ + isubxin:ix * xrange_ + isubxin + nblockx, iy * yrange + isubyin:iy * yrange + isubyin+nblocky, iz * zrange + isubzin:iz * zrange + isubzin+nblockz] += energy_dev
                    tot_energy_out[ix * xrange_ + isubxin:ix * xrange_ + isubxin + nblockx, iy * yrange + isubyin:iy * yrange + isubyin+nblocky, iz * zrange + isubzin:iz * zrange + isubzin+nblockz] += tot_energy
                    n_comp_out[ix * xrange_ + isubxin:ix * xrange_ + isubxin + nblockx, iy * yrange + isubyin:iy * yrange + isubyin+nblocky, iz * zrange + isubzin:iz * zrange + isubzin+nblockz] += n_components
                    likelihood_out[ix * xrange_ + isubxin:ix * xrange_ + isubxin + nblockx, iy * yrange + isubyin:iy * yrange + isubyin+nblocky, iz * zrange + isubzin:iz * zrange + isubzin+nblockz] += likelihood_
                    gmm_model_out['i{0}xj{1}'.format(ix * xrange_ + isubxin, iy * yrange + isubyin)] = gmm_model_
                    aic_bic_out['i{0}xj{1}'.format(ix * xrange_ + isubxin, iy * yrange + isubyin)] = aic_bic_

gmm_model_list = []
aic_bic_list = []

# MPI synchro
if rank == 0:
    gmm_model_list += [gmm_model_out]
    aic_bic_list += [aic_bic_out]
    for i in range(1, size):
        edrop_in = edrop_out * 0.0
        tot_th_in = tot_th_out * 0.0
        edev_in = edev_out * 0.0
        tot_energy_in = tot_energy_out * 0.0
        n_comp_in = n_comp_out * 0.0
        likelihood_in = likelihood_out * 0.0
        gmm_model_in = {}
        #MPI receive
        comm.Recv(edrop_in, source=i, tag=666)
        comm.Recv(tot_th_in, source=i, tag=667)
        comm.Recv(edev_in, source=i, tag=668)
        comm.Recv(tot_energy_in, source=i, tag=669)
        comm.Recv(n_comp_in, source=i, tag=670)
        gmm_model_in = comm.recv(source=i, tag=671)
        aic_bic_in = comm.recv(source=i, tag=672)
        comm.Recv(likelihood_in, source=i, tag=673)
        edrop_out += edrop_in
        tot_th_out += tot_th_in
        edev_out += edev_in
        tot_energy_out += tot_energy_in
        n_comp_out += n_comp_in
        gmm_model_list += [gmm_model_in]
        aic_bic_list += [aic_bic_in]
        likelihood_out += likelihood_in
        print('concluded communication iteration=', icount)
        sys.stdout.flush()
    pita_bread = np.zeros((nxc, nyc))
    pita_bread[:, :] = edrop_out[:, :, 0]
    print('size', pita_bread.shape[0], pita_bread.shape[0])
    file2 = h5py.File(file_output, 'w')
    file2.create_dataset(str(species) + 'energy_drop', (nxc, nyc, nzc), data=edrop_out)
    file2.create_dataset(str(species) + 'thermal_energy', (nxc, nyc, nzc), data=tot_th_out)
    file2.create_dataset(str(species) + 'energy_deviation', (nxc, nyc, nzc), data=edev_out)
    file2.create_dataset(str(species) + 'total_energy', (nxc, nyc, nzc), data=tot_energy_out)
    file2.create_dataset(str(species) + 'n_comp', (nxc, nyc, nzc), data=n_comp_out)
    file2.create_dataset(str(species) + 'likelihood', (nxc, nyc, nzc), data=likelihood_out)
    file2.close()

    gmm_model = {k: v for d in gmm_model_list for k, v in d.items()}
    aic_bic_fig = {k: v for d in aic_bic_list for k, v in d.items()}
    # Write GMM models and AIC/BIC values
    if not os.path.exists(gmm_dir_name):
        os.mkdir(gmm_dir_name)
        dump(gmm_model, '{0}/{1}_{2}_gmm_{3}_{4}x{5}.joblib'.format(gmm_dir_name, species, time_step, estimator, nxc, nyc))
    else:
        dump(gmm_model, '{0}/{1}_{2}_gmm_{3}_{4}x{5}.joblib'.format(gmm_dir_name, species, time_step, estimator, nxc, nyc))

    if not os.path.exists(aic_bic_dir_name):
        os.mkdir(aic_bic_dir_name)
        dump(aic_bic_fig, '{0}/{1}_{2}_{3}x{4}.joblib'.format(aic_bic_dir_name, species, time_step, nxc, nyc))
    else:
        dump(aic_bic_fig, '{0}/{1}_{2}_{3}x{4}.joblib'.format(aic_bic_dir_name, species, time_step, nxc, nyc))

# Send values to proc 0
else:
    comm.Send(edrop_out, dest=0, tag=666)
    comm.Send(tot_th_out, dest=0, tag=667)
    comm.Send(edev_out, dest=0, tag=668)
    comm.Send(tot_energy_out, dest=0, tag=669)
    comm.Send(n_comp_out, dest=0, tag=670)
    comm.send(gmm_model_out, dest=0, tag=671)
    comm.send(aic_bic_out, dest=0, tag=672)
    comm.Send(likelihood_out, dest=0, tag=673)
