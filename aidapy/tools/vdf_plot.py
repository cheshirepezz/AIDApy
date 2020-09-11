"""Methods for plotting interpolated VDFs products, from data or simulation.
Etienne Behar.
"""

import numpy as np
import matplotlib.pyplot as plt


def spher(vdf, grid_cart, plt_contourf=False, cmap='RdBu_r'):
    '''
    Plots the VDF interpolated over a spherical grid-of-interest, cylindrical symmetry.
    Meant for electrons in a magnetic field aligned frame.
    '''
    #
    np.seterr(divide='ignore')

    # Time averages:
    a0 = np.nanmean(vdf, axis=2)
    resolution = a0.shape[0]
    ind_mid = int(resolution/2.)
    #
    vdf_scaled = vdf.copy()
    vdf_scaled -= np.nanmin(vdf_scaled[:, :], axis=(1, 2))[:, None, None]
    vdf_scaled /= np.nanmax(vdf_scaled[:, :], axis=(1, 2))[:, None, None]
    b0 = np.nanmean(vdf_scaled, axis=2)
    levels0 = np.linspace(0, 1, 40)
    #
    distrib_normed = vdf.copy()
    mm = np.nanmean(distrib_normed[:, ind_mid-2:ind_mid+2], axis=(1, 2))[:, None, None]
    distrib_normed /= mm
    b1 = np.nanmean(distrib_normed, axis=2)
    b1 = np.log10(b1)
    vlim = max(-1.*np.nanmin(b1[b1 != -np.inf]), np.nanmax(b1[b1 != np.inf]))#*.6
    levels1 = np.linspace(-vlim, vlim, 40)
    #_________________________________

    fig, AX = plt.subplots(1, 3, figsize=(13, 9), sharex=True, sharey=True)
    for ax in AX:
        ax.set_aspect('equal')

    x = grid_cart[0, :, :, 0]
    y = grid_cart[2, :, :, 0]

    if plt_contourf:
        m0 = AX[0].contourf(x, y, np.log10(a0), 60, cmap=cmap, zorder=-20)
    else:
        m0 = AX[0].pcolormesh(x, y, np.log10(a0), cmap=cmap,
                              rasterized=True)
    AX[0].contour(x, y, np.log10(a0), 10, colors='k', linewidths=.5)

    if plt_contourf:
        m1 = AX[1].contourf(x, y, b0, levels0, cmap=cmap, zorder=-20)
        m2 = AX[2].contourf(x, y, b1, levels1,
                            cmap=cmap, zorder=-20)
    else:
        m1 = AX[1].pcolormesh(x, y, b0, vmin=0, vmax=1, cmap=cmap,
                              rasterized=True)
        m2 = AX[2].pcolormesh(x, y, b1, vmin=-vlim, vmax=vlim,
                              cmap=cmap, rasterized=True)

    AX[0].set_xlabel('v_perp')
    AX[0].set_ylabel('v_para')
    AX[0].set_title('Interpolated VDF')
    AX[1].set_xlabel('v_perp')
    AX[1].set_title('0-to-1 scaled')
    AX[2].set_xlabel('v_perp')
    AX[2].set_title('Normalised')

    fig.suptitle('Spherical coordinate system, cylindrical representation')

    posAx = AX[0].get_position()
    cax = fig.add_axes([posAx.x1-.02, posAx.y0+.5, .008, 0.2])
    cb = fig.colorbar(m0, cax=cax, orientation='vertical')
    # cb.set_ticks([-13,-16,-19])
    cb.set_label('VDF (s^3/m^6)')
    AX[0].set_title('Original VDF')
    #
    posAx = AX[1].get_position()
    cax = fig.add_axes([posAx.x1-.02, posAx.y0+.5, .008, 0.2])
    cb = fig.colorbar(m1, cax=cax, orientation='vertical')
    cb.set_ticks([0., .5, 1.])
    AX[1].set_title('Scaled VDF')
    #
    posAx = AX[2].get_position()
    cax = fig.add_axes([posAx.x1-.02, posAx.y0+.5, .008, 0.2])
    cb = fig.colorbar(m2, cax=cax, orientation='vertical')
    vlim = .1*np.floor(vlim*10.)
    cb.set_ticks([-vlim, 0., vlim])
    AX[2].set_title('Normalised VDF')

    if plt_contourf:
        for ax in AX:
            ax.set_rasterization_zorder(-10)

    set_spines(AX)
    plt.tight_layout()
    plt.show()

def cart(vdf, grid_cart, plt_contourf=False, cmap='RdBu_r'):
    """
    Plots the VDF interpolated over a cartesian grid-of-interest, cuts.
    """
    np.seterr(divide='ignore')

    resolution = vdf.shape[0]
    ind_mid = int(resolution/2.)

    centers_x = grid_cart[0, :, 0, 0]
    dX = centers_x[1]-centers_x[0]
    edges_x = centers_x-.5*dX
    edges_x = np.append(edges_x, edges_x[-1]+dX)
    x = centers_x
    y = centers_x

    a0 = np.log10(vdf[:, :, ind_mid])
    a1 = np.log10(vdf[:, ind_mid, :])
    a2 = np.log10(vdf[ind_mid, :, :])

    vlima = max(np.amax(a0), np.amax(a1), np.amax(a2))

    fig, AX = plt.subplots(1, 3, figsize=(16, 8), sharex=True, sharey=True)
    plt.subplots_adjust(top=.99, bottom=.03, left=.03, right=.99,
                        wspace=0., hspace=0.)
    for ax in AX.flatten():
        ax.set_aspect('equal')

    if plt_contourf:
        m0 = AX[0].contourf(centers_x, centers_x, a0.T, 60,
                            cmap=cmap, zorder=-20)
        AX[1].contourf(centers_x, centers_x, a1.T, 60,
                       cmap=cmap, zorder=-20)
        AX[2].contourf(centers_x, centers_x, a2.T, 60,
                       cmap=cmap, zorder=-20)
    else:
        m0 = AX[0].pcolormesh(edges_x, edges_x, a0.T,
                              vmax=vlima, #vmin=-vlima,
                              cmap=cmap, rasterized=True)
                              # vmax=vlim,
                              # vmin=-16.5,vmax=-11.8,
        AX[1].pcolormesh(edges_x, edges_x, a1.T,
                         vmax=vlima, #vmin=-vlima,
                         cmap=cmap, rasterized=True)
                         # vmax=vlim,
                         # vmin=-16.5,vmax=-11.8,
        AX[2].pcolormesh(edges_x, edges_x, a2.T,
                         vmax=vlima, #vmin=-vlima,
                         cmap=cmap, rasterized=True)
                         # vmax=vlim,
                         # vmin=-16.5,vmax=-11.8,

    AX[0].contour(x, y, a0.T, levels=40, colors='k', linewidths=.5)
    AX[1].contour(x, y, a1.T, levels=40, colors='k', linewidths=.5)
    AX[2].contour(x, y, a2.T, levels=40, colors='k', linewidths=.5)

    posAx = AX[1].get_position()
    cax = fig.add_axes([posAx.x0*1.1, posAx.y0*.55, .2, 0.015])
    cb = fig.colorbar(m0, cax=cax, orientation='horizontal')
    cb.set_label('VDF (s^3/m^6)')
    AX[0].set_title('v_x, v_y')
    AX[1].set_title('v_x, v_z')
    AX[2].set_title('v_y, v_z')

    fig.suptitle('Cartesian coordinate system, cuts')

    for ax in AX.flatten():
        ax.axvline(0, color='k', linewidth=.5)
        ax.axhline(0, color='k', linewidth=.5)
        # ax.axhline(edges_x[120], color='k', linewidth=.5)
        # ax.axhline(edges_x[140], color='k', linewidth=.5)
        if plt_contourf:
            ax.set_rasterization_zorder(-10)

    plt.show()

def spher_time(vdf_interp, vdf_scaled, vdf_normed, grid_spher, time_interp,
               plt_contourf=False, cmap='RdBu_r'):
    """
    Plots the VDF interpolated over a spherical grid-of-interest,
    cylindrical symmetry,
    along time.
    Meant for electrons in a magnetic field aligned frame.
    """
    np.seterr(divide='ignore')

    # vdf_interp = self._obj['vdf_interp_time'].values
    # vdf_scaled = self._obj['vdf_scaled_time'].values
    # vdf_normed = self._obj['vdf_normed_time'].values
    # time_interp = self._obj['time_interp'].values
    resolution = vdf_interp.shape[1]

    centers_rho = grid_spher[0, :, 0, 0]
    centers_theta = grid_spher[1, 0, :, 0]

    x = time_interp
    y = centers_theta*180./np.pi

    fig, AX = plt.subplots(5, 1, figsize=(14, 9), sharex=True)
    # plt.subplots_adjust(left=0., bottom=0., right=1., top=1., wspace=0.)

    for i, ax in enumerate(AX):
        i_sta = i*int(resolution/len(AX))
        i_sto = (i+1)*int(resolution/len(AX))-1
        pad = np.nanmean(vdf_scaled[:, i_sta:i_sto], axis=(1))
        ax.text(time_interp[0], 140, '{}-{} m/s'.format(centers_rho[i_sta],
                                                        centers_rho[i_sto]),
                color='k')
        if plt_contourf:
            ax.contourf(x, y, pad.T, np.linspace(0, 1, 60),
                        cmap=cmap, zorder=-20)
        else:
            ax.pcolormesh(x, y, pad.T,
                          vmin=0, vmax=1,
                          cmap=cmap, rasterized=True)

    fig.suptitle('Spherical coordinate system, scaled pitch-angle'
                 ' distribution.')

    for ax in AX:
        if plt_contourf:
            ax.set_rasterization_zorder(-10)

    set_spines(AX)
    plt.show()

def profiles_1d(vdf, grid_spher):
    '''
    Plots the parallel and perpendicular profiles of the interpolated vdf.
    '''
    #
    np.seterr(divide='ignore')

    vdf_interp = np.nanmean(vdf, axis=2)
    resolution = vdf_interp.shape[0]
    wid = int(5.*resolution/180.)
    centers_rho = grid_spher[0, :, 0, 0]
    centers_theta = grid_spher[1, 0, :, 0]
    ind_mid_theta = int(.5*centers_theta.size)

    profile_para = np.nanmean(vdf_interp[:, :wid], axis=1)
    profile_antiPara = np.nanmean(vdf_interp[:, -wid:], axis=1)
    profile_perp = np.nanmean(vdf_interp[:, ind_mid_theta-wid:ind_mid_theta+wid], axis=1)
    profile_para[profile_para == 0.] = np.nan
    profile_antiPara[profile_antiPara == 0.] = np.nan
    profile_perp[profile_perp == 0.] = np.nan

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.plot(centers_rho, profile_para, c='r', label='para')
    ax.plot(centers_rho, profile_antiPara, '--', c='r', label='anti-para')
    ax.plot(centers_rho, profile_perp, c='b', label='perp')
    ax.set_xlabel('Velocity (m/s)')
    ax.set_ylabel('VDF (#/m^6/s^3)')
    ax.set_yscale('log')
    ax.legend()
    set_spines(ax)
    plt.tight_layout()
    plt.show()

def gyro(vdf, grid_spher, grid_cart, cmap='RdBu_r'):
    """ Original and scaled along gyro-angle (relevant if right frame used).
    """

    np.seterr(divide='ignore')

    vdf_interp = vdf.copy()
    vdf_scaled = vdf.copy()
    vdf_scaled -= np.nanmin(vdf_scaled[:, :], axis=(1, 2))[:, None, None]
    vdf_scaled /= np.nanmax(vdf_scaled[:, :], axis=(1, 2))[:, None, None]
    resolution = vdf_interp.shape[0]
    ind_mid = int(resolution/2.)
    centers_rho = grid_spher[0, :, 0, 0]
    centers_theta = grid_spher[1, 0, :, 0]
    centers_phi = grid_spher[2, 0, 0, :]
    v_max = centers_rho[-1]
    ind_mid_theta = int(.5*centers_theta.size)
    ind_quat_phi = int(.25*centers_phi.size)
    ind_quat_phi0 = 0
    ind_quat_phi1 = int(1.*ind_quat_phi)
    ind_quat_phi2 = int(2.*ind_quat_phi)
    ind_quat_phi3 = int(3.*ind_quat_phi)
    wid = int(20.*resolution/360.)

    a0 = vdf_interp.copy()
    #
    b0 = vdf.copy()
    levels0 = np.linspace(0, 1, 40)
    #
    c0 = np.zeros((resolution, resolution+1))
    c0[:, :-1] = np.nanmean(vdf_interp[:, ind_mid_theta-2:ind_mid_theta+2, :], axis=1)
    c0[:, -1] = c0[:, 0]
    c1 = np.nanmean(vdf_interp[:, :, ind_quat_phi0:ind_quat_phi0+wid], axis=2)
    c2 = np.nanmean(vdf_interp[:, :, ind_quat_phi1:ind_quat_phi1+wid], axis=2)
    c3 = np.nanmean(vdf_interp[:, :, ind_quat_phi2:ind_quat_phi2+wid], axis=2)
    c4 = np.nanmean(vdf_interp[:, :, ind_quat_phi3:ind_quat_phi3+wid], axis=2)
    #
    d0 = np.zeros((resolution, resolution+1))
    d0[:, :-1] = np.nanmean(vdf_scaled[:, ind_mid_theta-2:ind_mid_theta+2, :], axis=1)
    d0[:, -1] = d0[:, 0]
    d1 = np.nanmean(vdf_scaled[:, :, ind_quat_phi0:ind_quat_phi0+wid], axis=2)
    d2 = np.nanmean(vdf_scaled[:, :, ind_quat_phi1:ind_quat_phi1+wid], axis=2)
    d3 = np.nanmean(vdf_scaled[:, :, ind_quat_phi2:ind_quat_phi2+wid], axis=2)
    d4 = np.nanmean(vdf_scaled[:, :, ind_quat_phi3:ind_quat_phi3+wid], axis=2)


    theta_mid_ind = grid_spher[1, 0, ind_mid, 0]
    #x = grid_cart[0, :, ind_mid, :]*np.sin(theta_mid_ind)
    #y = grid_cart[1, :, ind_mid, :]*np.sin(theta_mid_ind)

    x = np.zeros((resolution, resolution+1))
    x[:, :-1] = grid_cart[0, :, ind_mid, :]*np.sin(theta_mid_ind)
    x[:, -1] = grid_cart[0, :, ind_mid, 0]*np.sin(theta_mid_ind)
    y = np.zeros((resolution, resolution+1))
    y[:, :-1] = grid_cart[1, :, ind_mid, :]*np.sin(theta_mid_ind)
    y[:, -1] = grid_cart[1, :, ind_mid, 0]*np.sin(theta_mid_ind)

    fig, AX = plt.subplots(2, 5, figsize=(18, 8))
    for ax in AX.flatten(): ax.set_aspect('equal')

    dx = x[1]-x[0]
    # x = np.append(x, x[-1]+dx)
    AX[0, 0] = plt.subplot(2, 5, 1)#, projection='polar')
    # m0 = ax0.pcolormesh(x, y, np.log10(c0),#np.linspace(-19,-12.5,100),
    #                 cmap=oC.bwr_2, rasterized=True)
    m0 = AX[0, 0].contourf(x, y, np.log10(c0), 40,#np.linspace(-19,-12.5,100),
                           cmap=cmap, zorder=-20)

    AX[1, 0] = plt.subplot(2, 5, 6)#, projection='polar')
    m5 = AX[1, 0].contourf(x, y, (d0), np.linspace(0, 1, 40),
                           cmap=cmap, zorder=-20)

    for ax in [AX[0, 0], AX[1, 0]]:
        ax.plot([x[0, ind_quat_phi0], x[-1, ind_quat_phi0]],
                [y[0, ind_quat_phi0], y[-1, ind_quat_phi0]], '--k', lw=1)
        ax.plot([x[0, ind_quat_phi0+wid], x[-1, ind_quat_phi0+wid]],
                [y[0, ind_quat_phi0+wid], y[-1, ind_quat_phi0+wid]], '--k', lw=1)
        ax.plot([x[0, ind_quat_phi1], x[-1, ind_quat_phi1]],
                [y[0, ind_quat_phi1], y[-1, ind_quat_phi1]], '--k', lw=1)
        ax.plot([x[0, ind_quat_phi1+wid], x[-1, ind_quat_phi1+wid]],
                [y[0, ind_quat_phi1+wid], y[-1, ind_quat_phi1+wid]], '--k', lw=1)
        ax.plot([x[0, ind_quat_phi2], x[-1, ind_quat_phi2]],
                [y[0, ind_quat_phi2], y[-1, ind_quat_phi2]], '--k', lw=1)
        ax.plot([x[0, ind_quat_phi2+wid], x[-1, ind_quat_phi2+wid]],
                [y[0, ind_quat_phi2+wid], y[-1, ind_quat_phi2+wid]], '--k', lw=1)
        ax.plot([x[0, ind_quat_phi3], x[-1, ind_quat_phi3]],
                [y[0, ind_quat_phi3], y[-1, ind_quat_phi3]], '--k', lw=1)
        ax.plot([x[0, ind_quat_phi3+wid], x[-1, ind_quat_phi3+wid]],
                [y[0, ind_quat_phi3+wid], y[-1, ind_quat_phi3+wid]], '--k', lw=1)

    x = grid_cart[0, :, :, 0]
    y = grid_cart[2, :, :, 0]

    m1 = AX[0, 1].contourf(x, y, np.log10(c1), 40,
                           cmap=cmap, zorder=-20)

    m6 = AX[1, 1].contourf(x, y, (d1), np.linspace(0, 1, 40),
                           cmap=cmap, zorder=-20)

    m2 = AX[0, 2].contourf(x, y, np.log10(c2), 40,
                           cmap=cmap, zorder=-20)

    m7 = AX[1, 2].contourf(x, y, (d2), np.linspace(0, 1, 40),
                           cmap=cmap, zorder=-20)

    m3 = AX[0, 3].contourf(x, y, np.log10(c3), 40,
                           cmap=cmap, zorder=-20)

    m8 = AX[1, 3].contourf(x, y, (d3), np.linspace(0, 1, 40),
                           cmap=cmap, zorder=-20)

    m4 = AX[0, 4].contourf(x, y, np.log10(c4), 40,
                           cmap=cmap, zorder=-20)

    m9 = AX[1, 4].contourf(x, y, (d4), np.linspace(0, 1, 40),
                           cmap=cmap, zorder=-20)

    fig.suptitle('Spherical coordinate system, checking gyrotropy.')

    posAx = AX[0, 1].get_position()
    cax = fig.add_axes([posAx.x1+.0, posAx.y0*1.2, .008, 0.1])
    cb = fig.colorbar(m1, cax=cax, orientation='vertical')
    cb.set_label('VDF log10(s^3/m^6)')
    # cb.set_ticks([-13,-16,-19])

    posAx = AX[1, 1].get_position()
    cax = fig.add_axes([posAx.x1+.0, posAx.y0*1.2, .008, 0.1])
    cb = fig.colorbar(m6, cax=cax, orientation='vertical')
    cb.set_ticks([0, .5, 1])

    for ax in AX.flatten():
        ax.set_rasterization_zorder(-10)

    set_spines(AX)
    plt.tight_layout()
    plt.show()

def set_spines(AX):
    """ Nicer plots IMHO, Etienne Behar.
    """
    try:  ## AX is a a single axis.
        AX.spines['right'].set_visible(False)
        AX.spines['top'].set_visible(False)
        AX.spines['left'].set_position(('outward', 10))
        AX.spines['bottom'].set_position(('outward', 10))
    except:
        try:
            for ax in AX:
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['left'].set_position(('outward', 10))
                ax.spines['bottom'].set_position(('outward', 10))
        except:
            for ax in AX.flatten():
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['left'].set_position(('outward', 10))
                ax.spines['bottom'].set_position(('outward', 10))
