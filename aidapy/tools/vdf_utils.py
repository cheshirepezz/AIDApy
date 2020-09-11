import numpy as np
import math
from scipy.interpolate import RegularGridInterpolator, NearestNDInterpolator, LinearNDInterpolator


class vdf():

    def __init__(self, v_max, resolution, coord_sys):

        self.grid_cart = None
        self.grid_spher = None
        self.dvvv = None
        self.vdf_interp = np.zeros((resolution,resolution,resolution))
        grid_cart, grid_spher,
        grid_cyl, dvvv = self.init_grid(v_max, resolution, coord_sys)
        self.grid_cart_t = self.grid_cart.copy()
        self.grid_spher_t = self.grid_spher.copy()
        self.nb_counts = np.zeros((resolution,resolution,resolution))

    def interpolate_cart_vdf(self, grid, vdf0, interpolate='near'):

        if interpolate == 'near':
            method_str = 'nearest'
        elif interpolate == 'lin':
            method_str = 'linear'

        if interpolate in ['near', 'lin']:
            if vdf0.ndim==2:
                interpFunc = RegularGridInterpolator( (grid[0,:,0], grid[1,0,:]), vdf0,
                                                        bounds_error=False, method=method_str,
                                                        fill_value=np.nan)
                d = interpFunc(self.grid_cart[[0,2],:,:,0].reshape(2,-1).T) ## Ugly AF.
                d = d.reshape((self.vdf_interp.shape[0],self.vdf_interp.shape[0]))
                self.vdf_interp = d[:,:,None]
            elif vdf0.ndim==3:
                interpFunc = RegularGridInterpolator( (grid[0,:,0,0], grid[1,0,:,0], grid[2,0,0,:]), vdf0,
                                                        bounds_error=False, method=method_str,
                                                        fill_value=np.nan)
                d = interpFunc(self.grid_cart.reshape(3,-1).T)
                self.vdf_interp = d.T.reshape(self.vdf_interp.shape)  ## (res,res,res)


        # #
        # elif interpolate=='cub':
        #     d  = np.zeros_like(gridCart[0]).flatten()
        #     ip = tricubic.tricubic(list(distribPeriod), [distribPeriod.shape[0],distribPeriod.shape[1],distribPeriod.shape[2]])
        #     deltaSpeed = (np.log10(pSet.speed[iS,1]/normTh)-np.log10(pSet.speed[iS,0]/normTh))
        #     ds = pSet.speed[iS,1:]/normTh-pSet.speed[iS,:-1]/normTh
        #     deltaTheta = pSet.theta[1]-pSet.theta[0]
        #     deltaPhi   = pSet.phi[iS,1]-pSet.phi[iS,0]
        #     vMinSpeed  = np.log10(pSet.speed[iS,0]/normTh)
        #     vMinTheta  = 0.
        #     vMinPhi    = 0.
        #
        #     # gridS[0] = np.log10(gridS[0]) ## gridS here becomes an array of bin index, to which the coordinate belongs.
        #     # gridS[0] = (gridS[0]-vMinSpeed)/deltaSpeed #+ 1.5
        #     bin = np.digitize(gridS[0], pSet.speed[iS]/normTh)-1
        #     gridS[0] = bin + (gridS[0]-pSet.speed[iS,bin]/normTh)/ds[bin]
        #     gridS[1] = (gridS[1]-vMinTheta)/deltaTheta + .5
        #     gridS[2] = (gridS[2]-vMinPhi)/deltaPhi + .5
        #     for i, node in enumerate(gridS.reshape((3,-1)).T):
        #         d[i] = ip.ip(list(node))
        #     # itkTmp = (d<0)
        #     d = d.reshape((resFinal,resFinal,resFinal))
        #     d[gridS[0]<0] = np.nan ## "fill_value". Should also be done for values larger than, and not only smaller than.
        #     # d[itkTmp] = 0
        #     # sys.exit()
        #
        #_________________

    def interpolate_spher_vdf(self, grid, vdf0, interpolate='near', psp=False):

        speed = grid[0,:,0,0][::-1].copy()
        theta = grid[1,0,:,0].copy()
        phi   = grid[2,0,0,:].copy()
        vdf0 = np.flip(vdf0, axis=(0))

        if interpolate == 'near':
            interp_method = 'nearest'
        elif interpolate == 'lin':
            interp_method = 'linear'

        # itk = self.grid_spher[2]>np.pi
        # self.grid_spher[2,itk] -= 2.*np.pi
        if psp:
            phi -= 60.*np.pi/180.
            phi %= 2.*np.pi
            self.grid_spher_t[2] -= 60.*np.pi/180
            self.grid_spher_t[2] %= 2.*np.pi

        # phiPeriod       = np.zeros(18)
        # phiPeriod[1:-1] = phi
        # phiPeriod[0]    = phi[-1]-2*np.pi
        # phiPeriod[-1]   = phi[0]+2*np.pi
        # thetaPeriod       = np.zeros(10)
        # thetaPeriod[1:-1] = theta
        # thetaPeriod[0]    = theta[-1]-np.pi
        # thetaPeriod[-1]   = theta[0]+np.pi
        # distribPeriod              = np.zeros((32,10,18))
        # distribPeriod[:,1:-1,1:-1] = vdf0
        # distribPeriod[:,1:-1,0]    = vdf0[:,:,-1]
        # distribPeriod[:,1:-1,-1]   = vdf0[:,:,0]
        # distribPeriod[:,0]         = np.nanmean(distribPeriod[:,1], axis=1)[:,None]
        # distribPeriod[:,9]         = np.nanmean(distribPeriod[:,8], axis=1)[:,None]
        # itkR = ~np.isnan(speed)

        # interpFunc = RegularGridInterpolator( (speed, thetaPeriod, phiPeriod),
        #                                         distribPeriod,
        #                                         bounds_error=False, method=interp_method,
        #                                         fill_value=np.nan)
        interpFunc = RegularGridInterpolator( (speed, theta, phi),
                                                vdf0,
                                                bounds_error=False, method=interp_method,
                                                fill_value=np.nan)
        d = interpFunc(self.grid_spher_t.reshape(3,-1).T)
        d = d.T.reshape(self.vdf_interp.shape)  ## (res,res,res)
        d[np.isnan(d)] = 0.
        self.nb_counts += (~np.isnan(d))
        self.vdf_interp += d



    def transform_grid(self, R=None, v=None, s=None):

        if R is not None:
            gc = self.grid_cart.copy()
            self.grid_cart_t = np.dot(R, gc.reshape(3,-1)).reshape(self.grid_cart.shape)

        if v is not None:
            self.grid_cart_t -= v[:,None,None,None]

        self.grid_spher_t = self.cart2spher(self.grid_cart_t)

        # if interpolate=='near':
        #     interpFunc = RegularGridInterpolator( (speed, thetaPeriod, phiPeriod),
        #                                             (distribPeriod),
        #                                             bounds_error=False, method='nearest',
        #                                             fill_value=np.nan)
        #     d = interpFunc(self.grid_spher_t.reshape(3,-1).T)
        #     d = d.T.reshape(self.vdf_interp.shape)  ## (res,res,res)
        #     d[np.isnan(d)] = 0.
        #     self.vdf_interp += d
        #     print(np.nanmin(d), np.nanmax(d))
        #
        #
        #
        # elif interpolate=='lin':
        #     interpFunc = RegularGridInterpolator( (speed, thetaPeriod, phiPeriod),
        #                                             (distribPeriod),
        #                                             bounds_error=False, method='linear',
        #                                             fill_value=np.nan)
        #     # interpFunc = RegularGridInterpolator( (speed, theta, phi),
        #     #                                         vdf0,
        #     #                                         bounds_error=False, method='linear',
        #     #                                         fill_value=np.nan)
        #     d = interpFunc(self.grid_spher_t.reshape(3,-1).T)
        #     d = d.T.reshape(self.vdf_interp.shape)  ## (res,res,res)
        #     d[np.isnan(d)] = 0.
        #     self.vdf_interp += d
        #
        # elif interpolate=='cub':
        #     d  = np.zeros_like(gridCart[0]).flatten()
        #     ip = tricubic.tricubic(list(distribPeriod), [distribPeriod.shape[0],distribPeriod.shape[1],distribPeriod.shape[2]])
        #     deltaSpeed = (np.log10(pSet.speed[iS,1]/normTh)-np.log10(pSet.speed[iS,0]/normTh))
        #     ds = pSet.speed[iS,1:]/normTh-pSet.speed[iS,:-1]/normTh
        #     deltaTheta = pSet.theta[1]-pSet.theta[0]
        #     deltaPhi   = pSet.phi[iS,1]-pSet.phi[iS,0]
        #     vMinSpeed  = np.log10(pSet.speed[iS,0]/normTh)
        #     vMinTheta  = 0.
        #     vMinPhi    = 0.
        #
        #     # gridS[0] = np.log10(gridS[0]) ## gridS here becomes an array of bin index, to which the coordinate belongs.
        #     # gridS[0] = (gridS[0]-vMinSpeed)/deltaSpeed #+ 1.5
        #     bin = np.digitize(gridS[0], pSet.speed[iS]/normTh)-1
        #     gridS[0] = bin + (gridS[0]-pSet.speed[iS,bin]/normTh)/ds[bin]
        #     gridS[1] = (gridS[1]-vMinTheta)/deltaTheta + .5
        #     gridS[2] = (gridS[2]-vMinPhi)/deltaPhi + .5
        #     for i, node in enumerate(gridS.reshape((3,-1)).T):
        #         d[i] = ip.ip(list(node))
        #     # itkTmp = (d<0)
        #     d = d.reshape((resFinal,resFinal,resFinal))
        #     d[gridS[0]<0] = np.nan ## "fill_value". Should also be done for values larger than, and not only smaller than.
        #     # d[itkTmp] = 0
        #     # sys.exit()

        # if psp:
        #     self.grid_spher_t[2] += 60.*np.pi/180
        #     self.grid_spher_t[2] %= 2.*np.pi
        #
        #_________________






def init_grid(v_max, resolution, grid_geom):
    """Here we define the bin edges and centers, depending on the chosen
    coordinate system."""
    if grid_geom == 'cart':
        edgesX = np.linspace(-v_max, v_max, resolution + 1,
                             dtype=np.float32)
        centersX = (edgesX[:-1] + edgesX[1:]) * .5
        # 3 x res x res_phi x res/2
        grid_cart = np.mgrid[-v_max:v_max:resolution*1j,
                             -v_max:v_max:resolution*1j,
                             -v_max:v_max:resolution*1j]
        grid_cart = grid_cart.astype(np.float32)
        grid_spher = cart2spher(grid_cart)
        grid_cyl = cart2cyl(grid_cart)
        dv = centersX[1]-centersX[0]
        dvvv = np.ones((resolution, resolution, resolution)) * dv ** 3

    elif grid_geom == 'spher':
        edges_rho = np.linspace(0, v_max, resolution + 1, dtype=np.float32)
        edges_theta = np.linspace(0, np.pi, resolution + 1,
                                  dtype=np.float32)
        edges_phi = np.linspace(0, 2*np.pi, resolution + 1,
                                dtype=np.float32)
        centers_rho = (edges_rho[:-1] + edges_rho[1:]) * .5
        centers_theta = (edges_theta[:-1] + edges_theta[1:]) * .5
        centers_phi = (edges_phi[:-1] + edges_phi[1:]) * .5
        grid_spher = np.mgrid[centers_rho[0]:centers_rho[-1]:centers_rho.size*1j,
                              centers_theta[0]:centers_theta[-1]:centers_theta.size*1j,
                              centers_phi[0]:centers_phi[-1]:centers_phi.size*1j]
        grid_spher = grid_spher.astype(np.float32)
        grid_cart = spher2cart(grid_spher)
        grid_cyl = cart2cyl(grid_cart)
        d_rho = centers_rho[1]-centers_rho[0]
        d_theta = centers_theta[1]-centers_theta[0]
        d_phi = centers_phi[1]-centers_phi[0]
        dv = centers_rho[1]-centers_rho[0]
        dvvv = np.ones((resolution, resolution, resolution)) \
        * centers_rho[:, None, None] * d_rho * d_theta * d_phi

    elif grid_geom == 'cyl':
        edges_rho = np.linspace(0, v_max, resolution+1, dtype=np.float32)
        edges_phi = np.linspace(0, 2*np.pi, resolution+1, dtype=np.float32)
        edges_z = np.linspace(-v_max, v_max, resolution+1, dtype=np.float32)
        centers_rho = (edges_rho[:-1]+edges_rho[1:])*.5
        centers_phi = (edges_phi[:-1]+edges_phi[1:])*.5
        centers_z = (edges_z[:-1]+edges_z[1:])*.5
        grid_cyl = np.mgrid[centers_rho[0]:centers_rho[-1]:centers_rho.size*1j,
                            centers_phi[0]:centers_phi[-1]:centers_phi.size*1j,
                            centers_z[0]:centers_z[-1]:centers_z.size*1j]
        grid_cyl = grid_cyl.astype(np.float32)
        grid_cart = cyl2cart(grid_cyl)
        grid_spher = cart2spher(grid_cart)
        dRho = centers_rho[1]-centers_rho[0]
        dPhi = centers_phi[1]-centers_phi[0]
        dZ = centers_z[1]-centers_z[0]
        dvvv = np.ones((resolution, resolution, resolution)) \
        * centers_rho[:, None, None]*dRho*dPhi*dZ

    return grid_cart, grid_spher, grid_cyl, dvvv


def spher2cart(v_spher):
    """Coordinate system conversion
    """
    v_cart = np.zeros_like(v_spher)
    v_cart[0] = v_spher[0] * np.sin(v_spher[1]) * np.cos(v_spher[2])
    v_cart[1] = v_spher[0] * np.sin(v_spher[1]) * np.sin(v_spher[2])
    v_cart[2] = v_spher[0] * np.cos(v_spher[1])

    return v_cart


def cart2spher(v_cart):
    """Coordinate system conversion
    """
    v_spher = np.zeros_like(v_cart)
    v_spher[0] = np.sqrt(np.sum(v_cart ** 2, axis=0))
    v_spher[1] = np.arccos(v_cart[2] / v_spher[0])
    v_spher[2] = np.arctan2(v_cart[1], v_cart[0])
    itm = (v_spher[2] < 0.)
    v_spher[2][itm] += 2*np.pi

    return v_spher


def cyl2cart(v_cyl):
    """Coordinate system conversion
    """
    v_cart = np.zeros_like(v_cyl)
    v_cart[0] = v_cyl[0]*np.cos(v_cyl[1])
    v_cart[1] = v_cyl[0]*np.sin(v_cyl[1])
    v_cart[2] = v_cyl[2].copy()

    return v_cart


def cart2cyl(v_cart):
    """Coordinate system conversion
    """
    v_cyl = np.zeros_like(v_cart)
    v_cyl[0] = np.sqrt(v_cart[0]**2+v_cart[1]**2)
    v_cyl[1] = np.arctan2(v_cart[1], v_cart[0])
    v_cyl[2] = v_cart[2].copy()
    itm = (v_cyl[1] < 0.)
    v_cyl[1][itm] += 2*np.pi

    return v_cyl


def R_2vect(vector_orig, vector_fin):
    """
    Taken from:
    https://github.com/Wallacoloo/printipi/blob/master/util/rotation_matrix.py
    Calculate the rotation matrix required to rotate from one vector to another.
    For the rotation of one vector to another, there are an infinit series of
    rotation matrices possible.  Due to axially symmetry, the rotation axis
    can be any vector lying in the symmetry plane between the two vectors.
    Hence the axis-angle convention will be used to construct the matrix
    with the rotation axis defined as the cross product of the two vectors.
    The rotation angle is the arccosine of the dot product of the two unit vectors.
    Given a unit vector parallel to the rotation axis, w = [x, y, z] and the rotation angle a,
    the rotation matrix R is::
              |  1 + (1-cos(a))*(x*x-1)   -z*sin(a)+(1-cos(a))*x*y   y*sin(a)+(1-cos(a))*x*z |
        R  =  |  z*sin(a)+(1-cos(a))*x*y   1 + (1-cos(a))*(y*y-1)   -x*sin(a)+(1-cos(a))*y*z |
              | -y*sin(a)+(1-cos(a))*x*z   x*sin(a)+(1-cos(a))*y*z   1 + (1-cos(a))*(z*z-1)  |


    Parameters
    ----------
    R
        The 3x3 rotation matrix to update.
    vector_orig
        The unrotated vector defined in the reference frame.
    vector_fin
        The rotated vector defined in the reference frame.
    """

    # Convert the vectors to unit vectors.
    vector_orig = vector_orig / np.linalg.norm(vector_orig)
    vector_fin = vector_fin / np.linalg.norm(vector_fin)

    # The rotation axis (normalised).
    axis = np.cross(vector_orig, vector_fin)
    axis_len = np.linalg.norm(axis)
    if axis_len != 0.0:
        axis = axis / axis_len

    # Alias the axis coordinates.
    x = axis[0]
    y = axis[1]
    z = axis[2]

    # The rotation angle.
    angle = math.acos(np.dot(vector_orig, vector_fin))

    # Trig functions (only need to do this maths once!).
    ca = np.cos(angle)
    sa = np.sin(angle)

    # Calculate the rotation matrix elements.
    Rot_mat = np.zeros((3, 3))
    Rot_mat[0, 0] = 1.0 + (1.0 - ca)*(x**2 - 1.0)
    Rot_mat[0, 1] = -z*sa + (1.0 - ca)*x*y
    Rot_mat[0, 2] = y*sa + (1.0 - ca)*x*z
    Rot_mat[1, 0] = z*sa+(1.0 - ca)*x*y
    Rot_mat[1, 1] = 1.0 + (1.0 - ca)*(y**2 - 1.0)
    Rot_mat[1, 2] = -x*sa+(1.0 - ca)*y*z
    Rot_mat[2, 0] = -y*sa+(1.0 - ca)*x*z
    Rot_mat[2, 1] = x*sa+(1.0 - ca)*y*z
    Rot_mat[2, 2] = 1.0 + (1.0 - ca)*(z**2 - 1.0)

    return Rot_mat
