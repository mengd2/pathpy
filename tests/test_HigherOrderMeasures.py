import pathpy as pp
import pytest


from pathpy import higher_order_measures


@pytest.mark.parametrize('k, e_sum, e_var', (
        (3, 27.5833333, 0.0085720486),
        (2, 55.0, 0.046875),
        (1, 55, 0.046875),
))
def test_closeness_centrality(random_paths, k, e_sum, e_var):
    import numpy as np
    p = random_paths(50, 0, 8)
    hon = pp.HigherOrderNetwork(p, k=k)
    closeness = higher_order_measures.closeness_centrality(hon)
    np_closeness = np.array(list(closeness.values()))
    assert np_closeness.sum() == pytest.approx(e_sum)
    assert np_closeness.var() == pytest.approx(e_var)


@pytest.mark.parametrize('k, norm, e_sum, e_var, e_max', (
        (2, False, 213.404507128, 43.674855957, 37.5657124911),
        (1, False, 2, 0.00694444, 0.333333333),
        (2, True, 5.68083215, 0.030949114, 1),
))
def test_betweenness_centrality(random_paths, norm, k, e_sum, e_var, e_max):
    import numpy as np
    p = random_paths(50, 0, 8)
    hon = pp.HigherOrderNetwork(p, k=k)
    betweenness = higher_order_measures.betweenness_centrality(hon, normalized=norm)
    values = np.array(list(betweenness.values()))
    assert values.sum() == pytest.approx(e_sum)
    assert max(values) == pytest.approx(e_max)
    assert values.var() == pytest.approx(e_var)


@pytest.mark.parametrize('k, sub, projection, e_sum, e_var', (
        (2, False, 'all', 2.030946758666, 0.0168478112),
        (1, False, 'scaled', 2.82310329017, 0.00047012207),
        (2, False, 'last', 1.7463870380802424, 0.0077742413305),
        (2, False, 'first', 1.7461339874793731, 0.0083696967427),
        (2, True, 'all', 2.030946758, 0.0168478112489),
        (1, True, 'scaled', 2.823103290, 0.0004701220779),
        (2, True, 'last', 1.746387038080242, 0.007774241),
        (2, True, 'first', 1.7461339874793727, 0.0083696967427313),
))
def test_eigen_centrality(random_paths, sub, projection, k, e_sum, e_var):
    import numpy as np
    p = random_paths(50, 0, 8)
    hon = pp.HigherOrderNetwork(p, k=k)
    eigen = higher_order_measures.eigenvector_centrality(hon, projection, sub)
    values = np.array(list(eigen.values()))
    assert values.sum() == pytest.approx(e_sum)
    assert values.var() == pytest.approx(e_var)


@pytest.mark.parametrize('k, sub, proj, e_sum, e_var', (
        (2, False, 'all', 1, 0.000399240558236),
        (1, False, 'scaled', 1, 6.111199022e-05),
        (2, False, 'scaled', 1, 0.00039924055823),
        (2, False, 'last', 1, 0.00045826544),
        (2, False, 'first', 1, 0.000345796913),
        (2, True, 'all', 1, 0.000399240558),
        (1, True, 'scaled', 1, 6.111199022e-05),
        (2, True, 'scaled', 1, 0.000399240558236666),
        (2, True, 'last', 1, 0.000458265),
        (2, True, 'first', 1, 0.0003457969),
))
def test_pagerank_centrality(random_paths, sub, proj, k, e_sum, e_var):
    import numpy as np
    p = random_paths(50, 0, 8)
    hon = pp.HigherOrderNetwork(p, k=k)
    page = higher_order_measures.pagerank(hon, include_sub_paths=sub, projection=proj)
    values = np.array(list(page.values()))
    assert values.sum() == pytest.approx(e_sum)
    assert values.var() == pytest.approx(e_var)


@pytest.mark.parametrize('k, sub, e_gap', (
        (2, False, 1e-9),
        (1, False, 1e-5),
        (2, True, 1),
))
def test_eigen_value_gap(random_paths, k, sub, e_gap):
    import numpy as np
    p = random_paths(90, 0, 20)
    hon = pp.HigherOrderNetwork(p, k=k)
    np.random.seed(0)
    eigen_gap = higher_order_measures.eigenvalue_gap(hon, include_sub_paths=sub)
    assert eigen_gap < e_gap


@pytest.mark.parametrize('k, norm, e_sum, e_var', (
        (3, True, 1, 0.0036494914419765924),
        (2, False, 2765.72998141474, 8.661474971012986),
        (1, True, 1, 0.04948386659908706),
))
def test_fiedler_vector_sparse(random_paths, k, norm, e_sum, e_var):
    import numpy as np
    import pathpy
    p = random_paths(90, 0, 20)
    hon = pp.HigherOrderNetwork(p, k=k)
    fv = pathpy.higher_order_measures.fiedler_vector_sparse(hon, normalized=norm)
    assert fv.var() == pytest.approx(e_var, rel=1e-8)
    assert np.sum(fv ** 2) == pytest.approx(e_sum)


@pytest.mark.parametrize('k, e_sum, e_var', (
        (3, 1, 0.003649586067168485),
        (2, (1.0000000000000002+0j), 0.0031136096467386416),
        (1, (-0.0009514819500764382+0.1190367717310192j), 0.049999999999999996),
))
def test_fiedler_vector_dense(random_paths, k, e_sum, e_var):
    import numpy as np
    import pathpy
    p = random_paths(90, 0, 20)
    hon = pp.HigherOrderNetwork(p, k=k)
    fv = pathpy.higher_order_measures.fiedler_vector_dense(hon)
    assert fv.var() == pytest.approx(e_var, rel=1e-8)
    assert np.sum(fv ** 2) == pytest.approx(e_sum)


@pytest.mark.parametrize('k, e_sum', (
        (3, 0.9967398214809227),
        (2, 0.24345712528855065),
        (1, 0.7143571081268268),
))
def test_algebraic_connectivity(random_paths, k, e_sum):
    import pathpy
    p = random_paths(120, 0, 40)
    hon = pp.HigherOrderNetwork(p, k=k)
    ac = pathpy.higher_order_measures.algebraic_connectivity(hon, lanczos_vectors=60, maxiter=40)
    assert ac == pytest.approx(e_sum, rel=1e-7)
