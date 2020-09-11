"""
Tool for density estimation using mixture Gaussian models (GMM) for simulation data.
See also AIDA paper: https://arxiv.org/abs/1910.10012
"""
import h5py
import numpy as np
from sklearn import mixture
from scipy.stats import moment


def clustering(X, estimator='bic'):
    ''' Performs the GMM on a cell within
    x0 and x1 for x component
    y0 and y1 for y component
    z0 and z1 for z component
    The number of PIC cell building the 'GMM cell' is given by coarse_level
    Estimator allows to chose between Bayesian Information Criterion (BIC),
    Aikaike Information Criterion (AIC) and constant number of components
    (fixed at 6)
    '''
    if X.size > 0:
        # Compute energy
        tot_energy = np.sum(np.sum(X*X, axis=0))
        tot_thermal = np.sum(moment(X, moment=2))

        if X.shape[0] == 1:
            X = np.vstack((X, X))

        # Compute the best number of components
        gmm_output = best_gmm(X, estimator=estimator)
        n_component = gmm_output['n_components']
        # Specific check for very few number of particles
        if n_component >= X.shape[0]:
            n_component = 1
        elif X.shape[0] == 0:
            # Fake inputs
            X = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2], [2, 2, 2],
                          [1, 1, 1], [0, 0, 0]])

        gmm = gmm_output['model']
        aic_bic = gmm_output['aic_bic']

        # Fit the GMM
        gmm.fit(X)
        likelihood = gmm.score(X)

        # Diagonal is specific for gmm with full covariances
        # Compute E_drop and E_dev (check paper)
        energy_drop_num = np.sum(np.sum(np.diagonal(gmm.covariances_, axis1=1, axis2=2) * gmm.weights_.reshape((1, -1)).T, axis=1))
        energy_dev_num = np.sum(np.sum(np.square(gmm.means_) * gmm.weights_.reshape((1, -1)).T - np.square(gmm.means_ * gmm.weights_.reshape((1, -1)).T), axis=1))

        if np.isclose(tot_thermal, 0.0):
            energy_drop = 0.0
            energy_dev = 0.0
        else:
            energy_drop = energy_drop_num / (tot_thermal)
            energy_dev = energy_dev_num / (tot_thermal)
    else:
        print('no particles in this region')
        energy_drop = 0.0
        energy_dev = 0.0
        tot_energy = 0.0
        tot_thermal = 0.0
        n_component = 0.0
        gmm = 0.0
        aic_bic = 0.0
        likelihood = 0.0
    return energy_drop, energy_dev, tot_energy, tot_thermal, n_component, gmm, aic_bic, likelihood


def best_gmm(X, estimator='bic'):
    ''' Determining what is the best gmm models.
    It trains the GMM with 1, 2, ..., 6 components and return the model with the
    lowest estimator balue (bic, aic, or cst)
    '''
    np.random.seed(0)
    best_gmm_output = {}
    cv_type = 'full'

    # Fixed the number of components to mimic non parametric density estimation
    if estimator == 'cst':
        n_component = 8
        if X.shape[0] <= 8 and X.shape[0] > 0:
            n_component = X.shape[0] - 1
        best_gmm_output['n_components'] = n_component
        best_gmm_output['model'] = mixture.GaussianMixture(n_components=n_component,
                                      covariance_type=cv_type).fit(X)
        best_gmm_output['aic_bic'] = 0
        best_gmm_output['fit_1_comp'] = mixture.GaussianMixture(n_components=1,
                                      covariance_type=cv_type).fit(X)
    # Determine the best GMM using BIC or AIC
    else:
        n_components_max = 6
        if X.shape[0] <= n_components_max and X.shape[0] > 0:
            n_components_max = 2
        n_components_range = range(1, n_components_max)

        gmm_models = [mixture.GaussianMixture(n_components=n_components_, covariance_type=cv_type).fit(X) for n_components_ in n_components_range]
        bic_values = [m.bic(X) for m in gmm_models]
        aic_values = [m.aic(X) for m in gmm_models]

        aic_bic_value = {'n_comp':  n_components_range,
                         'bic': np.array(bic_values),
                         'aic': np.array(aic_values)}

        if estimator == 'aic':
            index_best = np.argmin(np.array(aic_values))
        else:
            index_best = np.argmin(np.array(bic_values))
        best_gmm_output['n_components'] = n_components_range[index_best]
        best_gmm_output['model'] = gmm_models[index_best]
        best_gmm_output['aic_bic'] = aic_bic_value
        best_gmm_output['fit_1_comp'] = gmm_models[0]

    # return a dictionarry at the end
    return best_gmm_output


def leggi_h5(file_name):
    '''This function read the spatial location and velocity components of the particles within a subblock
    given in h5 format.
    '''
    # Read the h5 file. Define the variable name here.
    with h5py.File(file_name, 'r') as hf:
        q_p = np.array(hf.get('qp'))
        x_p = np.array(hf.get('xp'))
        y_p = np.array(hf.get('yp'))
        z_p = np.array(hf.get('zp'))
        # Magnetic field-aligned basis
        u_p = np.array(hf.get('v_para'))
        v_p = np.array(hf.get('v_perp_1'))
        w_p = np.array(hf.get('v_perp_2'))
    return q_p, x_p, y_p, z_p, u_p, v_p, w_p
