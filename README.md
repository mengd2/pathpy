<img src="https://github.com/IngoScholtes/pathpy/blob/master/pathpy_logo.png" width="300" alt="pathpy logo" />

# Introduction

`pathpy` is an OpenSource python package for the analysis of time series data on networks using **higher-order** and **multi-order** graphical models.

The package is specifically tailored to analyze temporal networks as well as sequential data that capture multiple short, independent paths observed in an underlying graph topology. 
Examples for data that can be analysed with `pathpy` include time-stamped social networks, user click streams in information networks, biological pathways, or traces of information propagating in social media. 
Unifying the analysis of pathways and temporal networks, `pathpy` provides various methods to extract time-respecting paths from time-stamped network data. 
It extends (and will eventually supersede) the package [`pyTempnets`](https://github.com/IngoScholtes/pyTempNets).

`pathpy` facilitates the analysis of temporal correlations in time series data on networks.
It uses a principled model selection technique to infer higher-order graphical representations that capture both topological and temporal characteristics. 
It specifically allows to answer the question when a network abstraction of time series data is justified and when higher-order network representations are needed.

The theoretical foundation of this package, **higher-order network models**, was developed in the following research works:

1. I Scholtes: [When is a network a network? Multi-Order Graphical Model Selection in Pathways and Temporal Networks](http://dl.acm.org/citation.cfm?id=3098145), In KDD'17 - Proceedings of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, Halifax, Nova Scotia, Canada, August 13-17, 2017
2. I Scholtes, N Wider, A Garas: [Higher-Order Aggregate Networks in the Analysis of Temporal Networks: Path structures and centralities](http://dx.doi.org/10.1140/epjb/e2016-60663-0), The European Physical Journal B, 89:61, March 2016
3. I Scholtes, N Wider, R Pfitzner, A Garas, CJ Tessone, F Schweitzer: [Causality-driven slow-down and speed-up of diffusion in non-Markovian temporal networks](http://www.nature.com/ncomms/2014/140924/ncomms6024/full/ncomms6024.html), Nature Communications, 5, September 2014
4. R Pfitzner, I Scholtes, A Garas, CJ Tessone, F Schweitzer: [Betweenness preference: Quantifying correlations in the topological dynamics of temporal networks](http://journals.aps.org/prl/abstract/10.1103/PhysRevLett.110.198701), Phys Rev Lett, 110(19), 198701, May 2013

`pathpy` extends this approach towards **multi-layer graphical models** that capture temporal correlations at multiple length scales simultaneously. 
An illustrative example for a collection of paths (left) and a multi-order graphical representation is shown below. 
All mathematical details of the framework can be found in this [recent research paper](http://dl.acm.org/citation.cfm?id=3098145).

[![Watch promotional video](https://img.youtube.com/vi/CxJkVrD2ZlM/0.jpg)](https://www.youtube.com/watch?v=CxJkVrD2ZlM)

<img src="https://github.com/IngoScholtes/pathpy/blob/master/multiorder.png" width="500" alt="Illustration of Multi-Order Model" />

# Download and installation

`pathpy` is pure python code. It has no platform-specific dependencies and should thus work on all platforms. 
It builds on `numpy` and `scipy`. 
The latest version of `pathpy` can be installed by typing:

`> pip install git+git://github.com/IngoScholtes/pathpy.git`

# Tutorial

A [comprehensive educational tutorial](https://ingoscholtes.github.io/pathpy/tutorial.html) which shows how you can use `pathpy` to analyze data on pathways and temporal networks is [available online](https://ingoscholtes.github.io/pathpy/tutorial.html).
Moreover, a tutorial which illustrates the abstraction of **higher-order networks** in the modeling of dynamical processes in temporal networks is [available here](https://www.sg.ethz.ch/team/people/ischoltes/research-insights/temporal-networks-demo/). 
The latter tutorial is based on the predecessor library [`pyTempNets`](https://github.com/IngoScholtes/pyTempNets). Most of its features have been ported to `pathpy`.

# Documentation

The code is fully documented via docstrings which are accessible through python's built-in help system. Just type `help(SYMBOL_NAME)` to see the documentation of a class or method. A [reference manual is available here](https://ingoscholtes.github.io/pathpy/hierarchy.html).

# Releases and Versioning

The first public beta release of pathpy (released February 17 2017) is [v1.0-beta](https://github.com/IngoScholtes/pathpy/releases/tag/v1.0-beta.1). 
Following versions are named MAJOR.MINOR.PATCH according to [semantic versioning](http://semver.org/). 
The date of each release is encoded in the PATCH version.

# Known issues

- Depending on whether or not `scipy` has been compiled with or without the numerics package `MKL`, considerable numerical differences can occur, e.g. for eigenvalue centralities, PageRank, and other measures that depend on the eigenvectors and eigenvalues of matrices. Please refer to `scipy.show_config()` to show compilation flags.
- Interactive visualizations in jupyter are currently only supported for juypter notebooks, stand-alone HTML files, and the jupyter display integrated in IDEs like Visual Studio Code (which we highly recommend to work with pathpy). Due to its new widget mechanism, interactive d3js visualizations are currently not available for jupyterLab. Due to the complex document object model generated by jupyter notebooks, visualization performance is best in stand-alone HTML files and in Visual Studio Code.
- The visualization of temporal networks currently does not support the drawing of edge arrows for directed edges. However, a powerful templating mechanism is available to support custom interactive and dynamic visualizations of temporal networks.
- The visualization of paths in terms of alluvial diagrams within Jupyter is currently unstable for networks with large delay. This is due to the asynchronous loading of external scripts.

# Acknowledgements

The research behind this data analysis framework was funded by the Swiss State Secretariat for Education, Research and Innovation [(Grant C14.0036)](https://www.sg.ethz.ch/projects/seri-information-spaces/). 
The development of this package was generously supported by the [MTEC Foundation](http://www.mtec.ethz.ch/research/support/MTECFoundation.html) in the context of the project [The Influence of Interaction Patterns on Success in Socio-Technical Systems: From Theory to Practice](https://www.sg.ethz.ch/projects/mtec-interaction-patterns/).

# Contributors

[Ingo Scholtes](http://www.ingoscholtes.net) (project lead, development)  
[Luca Verginer](https://www.verginer.eu/) (development, test suite integration)  

# Past Contributors

Roman Cattaneo (development)  
Nicolas Wider (testing)  

# Copyright

`pathpy` is licensed under the [GNU Affero General Public License](https://choosealicense.com/licenses/agpl-3.0/).

(c) Copyright ETH Zürich, Chair of Systems Design, 2015-2017
