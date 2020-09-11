"""
Unit tests for mms_vdf methods.
"""
import numpy as np
import pytest
import aidapy.tools.vdf_utils as vdfu


def test_init_grid():
    """Unit test on vdfu.init_grid method."""
    reso = 5
    grid_cart, grid_spher, grid_cyl, \
    dvvv = vdfu.init_grid(v_max=1., resolution=reso,
                          grid_geom='spher')
    assert grid_cart.shape == (3, reso, reso, reso)
    assert grid_spher.shape == (3, reso, reso, reso)
    assert grid_cyl.shape == (3, reso, reso, reso)
    assert dvvv.shape == (reso, reso, reso)
    # Testing that the grid values are strictly increasing.
    assert np.all(grid_spher[0][1:] > grid_spher[0][:-1])
    assert np.all(grid_spher[1][:, 1:] > grid_spher[1][:, :-1])
    assert np.all(grid_spher[2][:, :, 1:] > grid_spher[2][:, :, :-1])
    # Testing that grid_cart and grid_spher are one and the same grid.
    assert np.allclose(grid_spher, vdfu.cart2spher(grid_cart))
    assert np.allclose(grid_cyl, vdfu.cart2cyl(grid_cart))


def test_R_2vect():
    """Unit test on vdfu.R_2vect method."""
    vec_a = np.array([1, 0, 0])
    vec_b = np.array([0, 1, 0])
    R = vdfu.R_2vect(vec_a, vec_b)
    # Right shape.
    assert R.shape == (3, 3)
    # Rotation around z-axis.
    assert R[2, 2] == 1.


def test_spher2cart():
    """Unit test on vdfu.spher2cart method."""
    reso = 5
    grid_spher_dummy = np.ones((3, reso, reso, reso))
    grid_cart = vdfu.spher2cart(grid_spher_dummy)
    assert grid_cart.shape == (3, reso, reso, reso)
    assert np.allclose(grid_spher_dummy, vdfu.cart2spher(grid_cart))


def test_cart2spher():
    """Unit test on vdfu.cart2spher method."""
    reso = 5
    grid_cart_dummy = np.ones((3, reso, reso, reso))
    grid_spher = vdfu.cart2spher(grid_cart_dummy)
    assert grid_spher.shape == (3, reso, reso, reso)
    assert np.allclose(grid_cart_dummy, vdfu.spher2cart(grid_spher))


def test_cyl2cart():
    """Unit test on vdfu.cyl2cart method."""
    reso = 5
    grid_cart_dummy = np.ones((3, reso, reso, reso))
    grid_cyl = vdfu.cart2cyl(grid_cart_dummy)
    assert grid_cyl.shape == (3, reso, reso, reso)
    assert np.allclose(grid_cart_dummy, vdfu.cyl2cart(grid_cyl))


def test_cart2cyl():
    """Unit test on vdfu.cart2cyl method."""
    reso = 5
    grid_cyl_dummy = np.ones((3, reso, reso, reso))
    grid_cart = vdfu.cyl2cart(grid_cyl_dummy)
    assert grid_cart.shape == (3, reso, reso, reso)
    assert np.allclose(grid_cyl_dummy, vdfu.cart2cyl(grid_cart))
