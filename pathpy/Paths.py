# -*- coding: utf-8 -*-
"""
    pathpy is an OpenSource python package for the analysis of sequential data
    on pathways and temporal networks using higher- and multi order graphical models

    Copyright (C) 2016-2017 Ingo Scholtes, ETH Zürich

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Contact the developer:

    E-mail: ischoltes@ethz.ch
    Web:    http://www.ingoscholtes.net
"""

import numpy as _np
import collections as _co
import sys as _sys
import scipy.sparse.linalg as _sla

from pathpy.Log import Log, Severity
from pathpy.HigherOrderNetwork import HigherOrderNetwork


class Paths:
    """
    Instances of this class represent path statistics
    which can be analyzed using higher- and multi-order network
    models. The origin of the path statistics can be (i) n-gram
    files which provide us with a list of paths in terms of n-grams
    of varying lengths, or (ii) a temporal network instance which
    provides us with a set of time-respecting paths based on a
    given maximum time difference delta.
    """

    def __init__(self):
        """
        Creates an empty Paths object
        """

        # A dictionary of paths that has the following structure:
        # - paths[k] is a dictionary containing all paths of length k,
        #    indexed by a path tuple p = (u,v,w,...)
        # - for each tuple p of length k, paths[k][p] contains a tuple
        #    (i,j) where i refers to the number of times p occurs as a
        #    subpath of a longer path, and j refers to the number of times p
        #    occurs as a *real* or *longest* path (i.e. not being a subpath
        #    of a longer path)
        self.paths = _co.defaultdict(lambda: _co.defaultdict(lambda: _np.array([0.0, 0.0])))

        # The character used to separate nodes on paths
        self.separator = ','

        # This can be used to limit the calculation of sub path statistics to a given
        # maximum length. This is useful, as the statistics of sub paths of length k
        # are only needed to fit a higher-order model with order k. Hence, if we know
        # that the model selection is limited to a given maximum order K, we can safely
        #  set the maximum sub path length to K. By default, sub paths of any length
        # will be calculated. Note that, independent of the sub path calculation
        # longest path of any length will be considered in the likelihood calculation!
        self.maxSubPathLength = _sys.maxsize


    def summary(self):
        """

        Returns
        -------
        str
            Returns a string containing basic summary info of this Paths instance
        """
        total_paths = 0
        sub_path_sum = 0
        l_path_sum = 0
        max_path_length = 0
        average_length = 0
        nodes = set()
        for k in self.paths:
            for p in self.paths[k]:
                total_paths += self.paths[k][p].sum()
                sub_path_sum += self.paths[k][p][0]
                l_path_sum += self.paths[k][p][1]
                average_length += self.paths[k][p][1] * k
                for v in p:
                    nodes.add(v)
            if len(self.paths[k]) > 0:
                max_path_length = max(max_path_length, k)
        if l_path_sum > 0:
            average_length = average_length / l_path_sum

        summary_fmt = (
            "Total path count: \t\t{lpsum} \n"
            "[Unique / Sub paths / Total]: \t[{unique_paths} / {spsum} / {total_paths}]\n"
            "Nodes:\t\t\t\t{len_nodes} \n"
            "Edges:\t\t\t\t{len_first_path}\n"
            "Max. path length:\t\t{maxL}\n"
            "Avg path length:\t\t{avgL} \n"
        )

        k_path_info_fmt = 'Paths of length k = {k}\t\t{lpsum} ' \
                          '[ {unique_paths_longer} / {spsum} / {total_paths} ]\n'

        summary_info = {
            "lpsum": l_path_sum,
            "unique_paths": self.getUniquePaths(),
            "spsum": sub_path_sum,
            "total_paths": total_paths,
            "len_nodes": len(nodes),
            "len_first_path": len(self.paths[1]),
            "maxL": max_path_length,
            "avgL": average_length
        }

        summary = summary_fmt.format(**summary_info)

        for k in sorted(self.paths):
            total_paths = 0
            sub_path_sum = 0
            l_path = 0
            for p in self.paths[k]:
                total_paths += self.paths[k][p].sum()
                sub_path_sum += self.paths[k][p][0]
                l_path += self.paths[k][p][1]

            unique_paths = self.getUniquePaths(l=k, considerLongerPaths=False)
            k_info = k_path_info_fmt.format(
                k=k, lpsum=l_path, spsum=sub_path_sum, total_paths=total_paths,
                unique_paths_longer=unique_paths
            )
            summary += k_info

        return summary

    def getPathLengths(self):
        """compute the length of all paths

        Returns
        -------
        dict
            Returns a dictionary containing the distribution of path lengths
            in this Path object. In the returned dictionary, entry
            lengths ``k`` is a ``numpy.array`` ``x`` where
            ``x[0]`` is the number of sub paths with length ``k``, and ``x[1]``
            is the number of (longest) paths with length ``k``


        """
        lengths = _co.defaultdict(lambda: _np.array([0., 0.]))

        for k in self.paths:
            for p in self.paths[k]:
                lengths[k] += self.paths[k][p]
        return lengths

    def __add__(self, other):
        """

        Parameters
        ----------
        other : Paths

        Returns
        -------
        Paths
            Default operator +, which returns the sum of two Path objects
        """
        p_sum = Paths()
        for l in self.paths:
            for p in self.paths[l]:
                p_sum.paths[l][p] = self.paths[l][p]
        for l in other.paths:
            for p in other.paths[l]:
                p_sum.paths[l][p] += other.paths[l][p]
        return p_sum


    def getSequence(self, stopchar='|'):
        """

        Parameters
        ----------
        stopchar : str
            the character used to separate paths

        Returns
        -------
        tuple:
            Returns a single sequence in which all paths have been concatenated.
            Individual paths are separated by a stop character.
        """
        Log.add('Concatenating paths to sequence ...')
        sequence = []
        for l in self.paths:
            for p in self.paths[l]:
                segment = []
                for s in p:
                    segment.append(s)
                if not stopchar == '':
                    segment.append(stopchar)
                for f in range(int(self.paths[l][p][1])):
                    sequence += segment

        Log.add('finished')
        return sequence

    def getUniquePaths(self, l=0, considerLongerPaths=True):
        """Returns the number of unique paths of a given length l (and possibly longer)

        Parameters
        ----------
        l : int
            the (inclusive) maximum length up to which path shall be counted.
        considerLongerPaths : bool
            TODO: add parameter description

        Returns
        -------
        int
            number of unique paths satisfying parameter ``l``
        """
        L = 0.0
        lmax = l
        if considerLongerPaths:
            if self.paths:
                lmax = max(self.paths)
            else:
                lmax = 0
        for j in range(l, lmax+1):
            for p in self.paths[j]:
                if self.paths[j][p][1] > 0:
                    L += 1.0
        return L

    def __str__(self):
        """
        Returns the default string representation of
        this Paths instance
        """
        return self.summary()


    def readEdges(filename, separator=',', weight=False, undirected=False,
                  maxlines=None, expandSubPaths=True, maxSubPathLength=None):
        """Read path in edgelist format

        Reads data from a file containing multiple lines of *edges* of the
        form "v,w,frequency,X" (where frequency is optional and X are
        arbitrary additional columns). The default separating character ','
        can be changed. In order to calculate the statistics of paths of any length,
        by default all subpaths of length 0 (i.e. single nodes) contained in an edge
        will be considered.

        Parameters
        ----------
        filename : str
            path to edgelist file
        separator : str
            character separating the nodes
        weight : bool
            is a weight given? if ``True`` it is the last element in the edge
            (i.e. ``a,b,2``)
        undirected : bool
            are the edges directed or undirected
        maxlines : int
            number of lines to read (useful to test large files)
        expandSubPaths : bool
        maxSubPathLength : int (default None)
            maximum length for subpaths to consider, ``None`` means the entire file is read

        Returns
        -------
        Paths
            a ``Paths`` object obtained from the edgelist
        """
        p = Paths()

        p.separator = separator
        p.maxSubPathLength = _sys.maxsize

        with open(filename, 'r') as f:
            Log.add('Reading edge data ... ')
            for n, line in enumerate(f):
                fields = line.rstrip().split(separator)
                assert len(fields) >= 2, 'Error: malformed line: {0}'.format(line)
                path = (fields[0], fields[1])
                if weight:
                    frequency = int(fields[2])
                else:
                    frequency = 1
                p.paths[1][path] += (0, frequency)
                if undirected:
                    reverse_path = (fields[1], fields[0])
                    p.paths[1][reverse_path] += (0, frequency)

                if maxlines is not None and n >= maxlines:
                    continue
        if expandSubPaths:
            p.expandSubPaths()
        Log.add('finished.')

        return p


    @classmethod
    def readFile(cls, filename, separator=',', pathFrequency=False, maxlines=_sys.maxsize,
                 maxN=_sys.maxsize, expandSubPaths=True, maxSubPathLength=_sys.maxsize):
        """Read path data in ngram format.

        Reads path data from a file containing multiple lines of n-grams of the form
        ``a,b,c,d,frequency`` (where frequency is optional).
        The default separating character ',' can be changed. Each n-gram will be interpreted as a path of
        length n-1, i.e. bigrams a,b are considered as path of length one, trigrams a,
        b,c as path of length two, etc. In order to calculate the statistics of paths
        of any length, by default all subpaths of length k < n-1 contained in an n-gram
        will be considered. I.e. for n=4 the four-gram a,b,c,d will be considered as a
        single (longest) path of length n-1 = 3 and three subpaths a->b, b->c, c->d of
        length k=1 and two subpaths a->b->c amd b->c->d of length k=2 will be
        additionally counted.

        Parameters
        ----------
        filename : str
            path to the n-gram file to read the data from
        separator : str
            the character used to separate nodes on the path, i.e. using a
            separator character of ';' n-grams are represented as ``a;b;c;...``
        pathFrequency : bool
            if set to ``True``, the last entry in each n-gram will be interpreted as
            weight (i.e. frequency of the path), e.g. ``a,b,c,d,4`` means that four-gram
            ``a,b,c,d`` has weight four. ``False`` by default, which means each path
            occurrence is assigned a default weight of 1 (adding weights for multiple
            occurrences).
        maxlines : int
            number of lines/n-grams to read, if left at None the whole file is read in.
        maxN : int
            The maximum n for the n-grams to read, i.e. setting maxN to 15 will ignore
            all n-grams of length 16 and longer, which means that only paths up to length
            n-1 are considered.
        expandSubPaths : bool
            by default all subpaths of the given n-grams are generated, i.e.
            for an input file with a single trigram a;b;c a path a->b->c of length two
            will be generated as well as two subpaths a->b and b->c of length one
        maxSubPathLength : int

        Returns
        -------
        Paths
            a ``Paths`` object obtained from the n-grams file
        """
        assert filename is not "", 'Empty filename given'

        # If subpath expansion is applied, we keep the information how many times a path
        # has been observed as a subpath, and how many times as a "real" path

        p = cls()

        p.maxSubPathLength = maxSubPathLength
        p.separator = separator
        maxL = 0

        with open(filename, 'r') as f:
            Log.add('Reading ngram data ... ')
            line = f.readline()
            n = 1
            while line and n <= maxlines:
                fields = line.rstrip().split(separator)
                path = ()
                # Add frequency of "real" path to second component of occurrence counter
                if pathFrequency:
                    for i in range(0, len(fields)-1):
                        # Omit empty fields
                        v = fields[i].strip()
                        if len(v) > 0:
                            path += (v,)
                    frequency = float(fields[len(fields)-1])
                    if len(path) <= maxN:
                        p.paths[len(path)-1][path] += (0, frequency)
                        maxL = max(maxL, len(path)-1)
                    else: # cut path at maxN
                        p.paths[maxN-1][path[:maxN]] += (0, frequency)
                        maxL = max(maxL, maxN-1)
                else:
                    for i in range(0, len(fields)):
                        # Omit empty fields
                        v = fields[i].strip()
                        if len(v) > 0:
                            path += (v,)
                    if len(path) <= maxN:
                        p.paths[len(path)-1][path] += (0, 1)
                        maxL = max(maxL, len(path)-1)
                    else: # cut path at maxN
                        p.paths[maxN-1][path[:maxN]] += (0, 1)
                        maxL = max(maxL, maxN-1)
                line = f.readline()
                n += 1
        # end of with open()
        Log.add('finished. Read ' + str(n-1) + ' paths with maximum length ' + str(maxL))

        if expandSubPaths:
            p.expandSubPaths()
        Log.add('finished.')

        return p


    def writeFile(self, filename, separator=','):
        """
        Writes path statistics data to a file.
        Each line in this file captures a longest path
        (v0,v1,...,vl), as well as its frequency f as follows

        v0,v1,...,vl,f

        @param filename: name of the file to write to
        @param separator: character that shall be used to
            separate nodes and frequencies
        """
        with open(filename, 'w') as f:
            for l in self.paths:
                for p in self.paths[l]:
                    if self.paths[l][p][1] > 0:
                        line = ""
                        for x in p:
                            line += x
                            line += separator
                        line += str(self.paths[l][p][1])
                        f.write(line+'\n')
        f.close()


    def ObservationCount(self):
        """
        Returns the total number of observed pathways of any length
        (includes multiple observations for paths with a frequency weight)
        """

        sum = 0
        for k in self.paths:
            for p in self.paths[k]:
                sum += self.paths[k][p][1]
        return sum


    def expandSubPaths(self):
        """
        This function implements the sub path expansion, i.e.
        for a four-gram a,b,c,d, the paths a->b, b->c, c->d of
        length one and the paths a->b->c and b->c->d of length
        two will be counted.

        This process will consider restrictions to the maximum
        sub path length defined in self.maxSubPathLength
        """

        # nothing to see here ...
        if len(self.paths) == 0:
            return

        Log.add('Calculating sub path statistics ... ')

        # the expansion of all subpaths in paths with a maximum path length of maxL
        # necessarily generates paths of *any* length up to MaxL.
        # Forcing the generation of all these indices here, prevents us
        # from mutating indices during subpath creation. The fact that indices are
        # immutable allows us to use efficient iterators and prevent unnecessarily copying

        # Thanks to the use of defaultdict, the following trick will prevent us from
        # repeatedly testing whether l already exists as a key
        for l in range(max(self.paths)):
            self.paths[l] = self.paths[l]

        # expand subpaths in paths of any length ...
        for pathLength in self.paths:
            for path in self.paths[pathLength]:

                # The frequency is given by the number of occurrences as longest
                # path, which is stored in the second entry of the numpy array
                frequency = self.paths[pathLength][path][1]

                # compute maximum length of sub paths to consider
                # (maximum up to pathLength)
                maxL = min(self.maxSubPathLength+1, pathLength)

                # Generate all subpaths of length k for k = 0 to k = maxL-1 (inclusive)
                for k in range(0, maxL):
                    # Generate subpaths of length k for all start indices s
                    # for s = 0 to s = pathLength-k (inclusive)
                    for s in range(0, pathLength-k+1):
                        # Add frequency as a subpath to *first* entry of occurrence
                        # counter
                        self.paths[k][path[s:s+k+1]] += (frequency, 0)


    def addPathTuple(self, path, expandSubPaths=True, frequency=(0, 1)):
        """
        Adds a tuple of elements as a path. If the elements are not strings,
        a conversion to strings will be made. This function can be used to
        to set custom subpath statistics, via the frequency tuple (see below).

        @param path: The path tuple to be added, e.g. ('a', 'b', 'c')
        @param expandSubPaths: Whether or not to calculate subpath statistics for this path
        @param frequency: A tuple (x,y) indicating the frequency of this path as subpath
            (first component) and longest path (second component). Default is (0,1).
        """

        assert len(path) > 0, 'Error: paths needs to contain at least one element'

        if type(path[0]) == str:
            path_str = path
        else:
            path_str = tuple(map(str, path))

        self.paths[len(path)-1][path_str] += frequency

        if expandSubPaths:

            maxL = min(self.maxSubPathLength+1, len(path_str)-1)

            for k in range(0, maxL):
                for s in range(len(path_str)-k):
                    # for all start indices from 0 to n-k

                    subpath = ()
                    # construct subpath
                    for i in range(s, s+k+1):
                        subpath += (path_str[i],)
                    # add subpath weight to first component of occurrences
                    self.paths[k][subpath] += (frequency[1], 0)



    def addPath(self, ngram, separator=',', expandSubPaths=True, frequency=None):
        """
        Adds the path(s) of a single n-gram to the path statistics object.

        @param ngram: An ngram representing a path between nodes, separated by the separator character, e.g.
            the 4-gram a;b;c;d represents a path of length three (with separator ';')

        @param separator: The character used as separator for the ngrams (';' by default)

        @param expandSubPaths: by default all subpaths of the given ngram are generated, i.e.
            for the trigram a;b;c a path a->b->c of length two will be generated
            as well as two subpaths a->b and b->c of length one

        @param frequency: the number of occurrences (i.e. frequency) of the ngram
        """

        fields = ngram.rstrip().split(separator)
        path = ()
        for i in range(0, len(fields)):
            path += (fields[i],)

        # add the occurrences as *longest* path to the second component of the numpy array
        if frequency != None:
            self.paths[len(path)-1][path] += (0, frequency)
        else:
            self.paths[len(path)-1][path] += (0, 1)

        if expandSubPaths:
            maxL = min(self.maxSubPathLength+1, len(path)-1)

            for k in range(0, maxL):
                for s in range(len(path)-k):
                    # for all start indices from 0 to n-k

                    subpath = ()
                    # construct subpath
                    for i in range(s, s+k+1):
                        subpath += (path[i],)
                    # add subpath weight to first component of occurrences
                    if frequency != None:
                        self.paths[k][subpath] += (frequency, 0)
                    else:
                        self.paths[k][subpath] += (1, 0)


    def getContainedPaths(p, node_filter):
        """
        Returns the set of maximum-length sub-paths of the path p, which
        only contain nodes that appear in the node_filter. As an example,
        for the path (a,b,c,d,e,f,g) and a node_filter [a,b,d,f,g], the method
        will return [(a,b), (d,), (f,g)].

        @param p: a path tuple to check for contained paths
        @param node_filter: a set of nodes to which the contained paths should be limited
        """
        contained_paths = []
        current_path = ()
        for k in range(0, len(p)):
            if p[k] in node_filter:
                current_path += (p[k],)
            else:
                if len(current_path) > 0:
                    contained_paths.append(current_path)
                    current_path = ()
        if len(current_path) > 0:
            contained_paths.append(current_path)

        return contained_paths


    def filterPaths(self, node_filter, minLength=0, maxLength=_sys.maxsize):
        """
        Returns a new paths object which contains only paths between nodes in a given
        filter set. For each of the paths in the current Paths object, the set of maximally
        contained subpaths between nodes in node_filter is extracted. This method is useful
        when studying (sub-)paths passing through a subset of nodes.

        @param node_filter: the nodes for which paths with be extracted from the current
            set of paths
        @param minLength: the minimum length of paths to extract (default 0)
        @param maxLength: the maximum length of paths to extract (default sys.maxsize)
        """

        p = Paths()
        for l in self.paths:
            for x in self.paths[l]:
                if self.paths[l][x][1] > 0:

                    # determine all contained subpaths which only pass through nodes in node_filter
                    contained = Paths.getContainedPaths(x, node_filter)
                    for s in contained:
                        if len(s)-1 >= minLength and len(s)-1 <= maxLength:
                            p.addPathTuple(s, expandSubPaths=True, frequency=(0, self.paths[l][x][1]))
        return p


    def projectPaths(self, mapping):
        """
        Returns a new path object in which nodes have been mapped to different labels
        given by an arbitrary mapping function. For instance, for the mapping
        {'a': 'x', 'b': 'x', 'c': 'y', 'd': 'y'} the path (a,b,c,d) is mapped to
        (x,x,y,y). This is useful, e.g., to map page page click streams to topic
        click streams, using a mapping from pages to topics.

        @param mapping: a dictionary that maps nodes to the new labels
        """
        p = Paths()
        p.maxSubPathLength = self.maxSubPathLength
        for l in self.paths:
            for x in self.paths[l]:
                # if this path ocurred as longest path
                if self.paths[l][x][1] > 0:
                    # construct projected path
                    newP = ()
                    for v in x:
                        newP += (mapping[v],)
                    # add to new path object and expand sub paths
                    p.addPathTuple(newP, expandSubPaths=True, frequency=(0, self.paths[l][x][1]))
        return p


    def getSlowDownFactor(self, k=2, lanczosVecs=15, maxiter=1000):
        """
        Returns a factor S that indicates how much slower (S>1) or faster (S<1)
        a diffusion process evolves in a k-order model of the path statistics
        compared to what is expected based on a first-order model. This value captures
        the effect of order correlations of length k on a diffusion process which evolves
        based on the observed paths.
        """

        assert k > 1, 'Slow-down factor can only be calculated for orders larger than one'

        # NOTE to myself: most of the time goes for construction of the 2nd order
        # NOTE            null graph, then for the 2nd order null transition matrix

        gk = HigherOrderNetwork(self, k=k)
        gkn = HigherOrderNetwork(self, k=k, nullModel=True)

        Log.add('Calculating slow down factor ... ', Severity.INFO)

        # Build transition matrices
        Tk = gk.getTransitionMatrix()
        Tkn = gkn.getTransitionMatrix()

        # Compute eigenvector sequences
        # NOTE: ncv=13 sets additional auxiliary eigenvectors that are computed
        # NOTE: in order to be more confident to find the one with the largest
        # NOTE: magnitude, see
        # NOTE: https://github.com/scipy/scipy/issues/4987
        w2 = _sla.eigs(Tk, which="LM", k=2, ncv=lanczosVecs, return_eigenvectors=False, maxiter=maxiter)
        evals2_sorted = _np.sort(-_np.absolute(w2))

        w2n = _sla.eigs(Tkn, which="LM", k=2, ncv=lanczosVecs, return_eigenvectors=False, maxiter=maxiter)
        evals2n_sorted = _np.sort(-_np.absolute(w2n))

        Log.add('finished.', Severity.INFO)

        return _np.log(_np.abs(evals2n_sorted[1]))/_np.log(_np.abs(evals2_sorted[1]))


    def getEntropyGrowthRateRatio(self, method='MLE', k=2, lanczosVecs=15, maxiter=1000):
        """
        Computes the ratio between the entropy growth rate ratio between
        the k-order and first-order model of a temporal network t. Ratios smaller
        than one indicate that the temporal network exhibits non-Markovian characteristics
        """

        # NOTE to myself: most of the time here goes into computation of the
        # NOTE            EV of the transition matrix for the bigger of the
        # NOTE            two graphs below (either 2nd-order or 2nd-order null)

        assert (method == 'MLE' or method == 'Miller'), 'Only methods MLE or Miller are supported'

        # Generate k-order network
        gk = HigherOrderNetwork(self, k=k)
        g1 = HigherOrderNetwork(self, k=1)

        Log.add('Calculating entropy growth rate ratio ... ', Severity.INFO)

        # Compute entropy growth rate of observed transition matrix
        A = g1.getAdjacencyMatrix(weighted=False, transposed=True)
        Tk = gk.getTransitionMatrix()
        Tk_pi = HigherOrderNetwork.getLeadingEigenvector(Tk, normalized=True, lanczosVecs=lanczosVecs, maxiter=maxiter)

        Tk.data *= _np.log2(Tk.data)

        # Apply Miller correction to the entropy estimation
        if method == 'Miller':
            # Here, K is the number of different k-paths that can exist based on the
            # observed edges
            K = (A**k).sum()
            print('K = ', K)

            # N is the number of observations used to estimate the transition probabilities
            # in the second-order network. This corresponds to the total edge weight in the
            # k-order network, or - alternatively - to the number of paths of length k
            N = 0
            for p in self.paths[k]:
                N += self.paths[k][p].sum()
            print('N = ', N)
            Hk = _np.sum(Tk * Tk_pi) + (K-1)/(2*N)
        else:
            # simple MLE estimation
            Hk = -_np.sum(Tk * Tk_pi)

        Hk = _np.absolute(Hk)

        # Compute entropy rate of null model
        gk_n = HigherOrderNetwork(self, k=k, nullModel=True)

        # For the entropy rate of the null model, no Miller correction is needed
        # since we assume that transitions correspond to the true probabilities
        Tk_n = gk_n.getTransitionMatrix()
        Tk_n_pi = HigherOrderNetwork.getLeadingEigenvector(Tk_n)
        Tk_n.data *= _np.log2(Tk_n.data)
        Hk_n = -_np.sum(Tk_n * Tk_n_pi)
        Hk_n = _np.absolute(Hk_n)

        Log.add('finished.', Severity.INFO)

        # Return ratio
        return Hk/Hk_n



    def BWPrefMatrix(self, v):
        """Computes a betweenness preference matrix for a node v

        @param v: Node for which the betweenness preference matrix shall
            be calculated
        """
        # create first-order network
        g = HigherOrderNetwork(self)

        indeg = len(g.predecessors[v])
        outdeg = len(g.successors[v])

        index_succ = {}
        index_pred = {}

        B_v = _np.zeros(shape=(indeg, outdeg))

        # Create an index-to-node mapping for predecessors and successors
        i = 0
        for u in g.predecessors[v]:
            index_pred[u] = i
            i = i+1

        i = 0
        for w in g.successors[v]:
            index_succ[w] = i
            i = i+1

        # Calculate entries of betweenness preference matrix
        for p in self.paths[2]:
            if p[1] == v:
                B_v[index_pred[p[0]], index_succ[p[2]]] += self.paths[2][p].sum()

        return B_v


    def __Entropy(prob, K=None, N=None, method='MLE'):
        """
        Calculates the entropy of an (observed) probability ditribution
        based on Maximum Likelihood Estimation (MLE) (default) or using
        a Miller correction.

        @param prob: the observed probabilities
        @param K: the number of possible outcomes, i.e. outcomes with non-zero probability to be used
            for the Miller correction (default None)
        @param N: number of samples based on which observed probabilities where computed. This
            is needed for the Miller correaction (default None)
        @param method: The method to be used to calculate entropy. Can be 'MLE' (default) or 'Miller'
        """

        if method == 'MLE':
            idx = _np.nonzero(prob)
            return -_np.inner(_np.log2(prob[idx]), prob[idx])
        elif method == 'Miller':
            assert K != None and N != None
            if N == 0:
                return 0
            else:
                idx = _np.nonzero(prob)
                return -_np.inner(_np.log2(prob[idx]), prob[idx]) + (K-1)/(2*N)


    def BetweennessPreference(self, v, normalized=False, method='MLE'):
        """
        Calculates the betweenness preferences of a
        node v based on the mutual information of path
        statistics of length two.

        @nornalized: whether or not to normalize betweenness preference values

        @method: which method to use for the entropy calculation. The default 'MLE' uses
            the standard Maximum-Likelihood estimation of entropy. Setting method to
            'Miller' additionally applies a Miller-correction. see e.g.
            Liam Paninski: Estimation of Entropy and Mutual Information, Neural Computation 5, 2003 or
            http://www.nowozin.net/sebastian/blog/estimating-discrete-entropy-part-2.html
        """

        assert method == 'MLE' or method == 'Miller'

        # If the network is empty, just return zero
        if len(self.getNodes()) == 0:
            return 0.0

        # First create the betweenness preference matrix (equation (2) of the paper)
        B_v = self.BWPrefMatrix(v)

        if B_v.shape[0] == 0 or B_v.shape[1] == 0:
            return None

        # Normalize matrix (equation (3) of the paper)
        # NOTE: P_v has the same shape as B_v
        P_v = _np.zeros(shape=B_v.shape)
        S = _np.sum(B_v)

        if S > 0:
            P_v = B_v / S

        # Compute marginal probabilities
        # Marginal probabilities P^v_d = \sum_s'{P_{s'd}}
        marginal_d = _np.sum(P_v, axis=0)

        # Marginal probabilities P^v_s = \sum_d'{P_{sd'}}
        marginal_s = _np.sum(P_v, axis=1)

        if method == 'Miller':

            # total number of samples, i.e. observed two-paths
            N = _np.sum(B_v)

            # print('N = ', N)
            # print('B = ', B_v)
            # print('marginal_s = ', marginal_s)
            # print('marginal_d = ', marginal_d)

            # marginal entropy H(S)
            H_s = Paths.__Entropy(marginal_s, len(marginal_s), N, method='Miller')

            # print('H(S) = ', H_s)
            # marginal entropy H(D)

            H_d = Paths.__Entropy(marginal_d, len(marginal_d), N, method='Miller')

            # print('H(D) = ', H_d)
            # we need the conditional entropy H(D|S)

            H_ds = 0
            for s in range(len(marginal_s)):

                # number of two paths s -> v -> * observed in the data
                N_s = _np.sum(B_v[s, :])

                # print('N(s=' + str(s) + ') = ' +  str(N_s))

                # probabilities of all destinations, given the particular source s
                p_ds = B_v[s, :]/_np.sum(B_v[s, :])

                # print('P(D|S=' + str(s) + ') = '+ str(p_ds))

                # number of possible destinations d
                K_s = len(p_ds)

                # print('K(s=' + str(s) + ') = ' +  str(K_s))

                # marginal_s[s] is the overall probability of source s
                p_s = marginal_s[s]

                # add to conditional entropy
                H_ds += p_s * Paths.__Entropy(p_ds, K_s, N_s, method='Miller')

                I = H_d - H_ds

            # print('H(D|S) = ', H_ds)

        else:
            # use MLE estimation
            H_s = Paths.__Entropy(marginal_s)
            H_d = Paths.__Entropy(marginal_d)
            # H_ds = 0

            # for s in range(len(marginal_s)):
            #    print('s = ' + str(s) + ': ' + str(_np.sum(P_v[s,:])))
            #    p_ds = P_v[s,:]/_np.sum(P_v[s,:])
            #    H_ds += marginal_s[s] * Paths.__Entropy(p_ds)

            # Alternative calculation (without explicit entropies)
            # build mask for non-zero elements
            row, col = _np.nonzero(P_v)
            pv = P_v[(row, col)]
            marginal = _np.outer(marginal_s, marginal_d)
            log_argument = _np.divide(pv, marginal[(row, col)])
            I = _np.dot(pv, _np.log2(log_argument))

        # I = H_d - H_ds

        if normalized:
            I = I/_np.min([H_s, H_d])

        return I


    def getNodes(self):
        """
        Returns the list of nodes for the underlying
        set of paths
        """
        nodes = set()
        for p in self.paths[0]:
            nodes.add(p[0])
        return nodes


    def getDistanceMatrix(self):
        """
        Calculates shortest path distances between all pairs of
        nodes based on the observed shortest paths (and subpaths)
        """
        shortest_path_lengths = _co.defaultdict(lambda: _co.defaultdict(lambda: _np.inf))

        Log.add('Calculating distance matrix based on empirical paths ...', Severity.INFO)
        # Node: no need to initialize shortest_path_lengths[v][v] = 0
        # since paths of length zero are contained in self.paths

        for l in self.paths:
            for p in self.paths[l]:
                start = p[0]
                end = p[-1]
                if l < shortest_path_lengths[start][end]:
                    shortest_path_lengths[start][end] = l

        Log.add('finished.', Severity.INFO)

        return shortest_path_lengths


    def getShortestPaths(self):
        """
        Calculates all observed shortest paths (and subpaths) between
        all pairs of nodes
        """
        shortest_paths = _co.defaultdict(lambda: _co.defaultdict(lambda: set()))
        shortest_path_lengths = _co.defaultdict(lambda: _co.defaultdict(lambda: _np.inf))

        Log.add('Calculating shortest paths based on empirical paths ...', Severity.INFO)

        for l in self.paths:
            for p in self.paths[l]:
                s = p[0]
                d = p[-1]
                # we found a path of length l from s to d
                if l < shortest_path_lengths[s][d]:
                    shortest_path_lengths[s][d] = l
                    shortest_paths[s][d] = set()
                    shortest_paths[s][d].add(p)
                elif l == shortest_path_lengths[s][d]:
                    shortest_paths[s][d].add(p)

        Log.add('finished.', Severity.INFO)

        return shortest_paths


    def BetweennessCentrality(self, normalized=False):
        """
        Calculates the betweenness centrality of nodes based on
        observed shortest paths between all pairs of nodes
        """

        node_centralities = _co.defaultdict(lambda: 0)
        shortest_paths = self.getShortestPaths()

        for s in shortest_paths:
            for d in shortest_paths[s]:
                for p in shortest_paths[s][d]:
                    for x in p[1:-1]:
                        if s != d != x:
                            # print('node ' + x + ': ' + str(1.0 / len(shortest_paths[start][end])))
                            node_centralities[x] += 1.0 / len(shortest_paths[s][d])
                            # node_centralities[x] += 1.0
        if normalized:
            m = max(node_centralities.values())
            for v in node_centralities:
                node_centralities[v] /= m

        # assign zero values to nodes not occurring on shortest paths
        nodes = self.getNodes()
        for v in nodes:
            node_centralities[v] += 0

        return node_centralities


    def ClosenessCentrality(self, normalized=False):
        """
        Calculates the closeness centrality of nodes based on
        observed shortest paths between all nodes
        """

        node_centralities = _co.defaultdict(lambda: 0)
        shortest_path_lengths = self.getDistanceMatrix()

        for x in shortest_path_lengths:
            for d in shortest_path_lengths[x]:
                if x != d and shortest_path_lengths[x][d] < _np.inf:
                    node_centralities[x] += 1.0 / shortest_path_lengths[x][d]

        # assign zero values to nodes not occurring
        nodes = self.getNodes()
        for v in nodes:
            node_centralities[v] += 0

        if normalized:
            m = max(node_centralities.values())
            for v in nodes:
                node_centralities[v] /= m

        return node_centralities

    def VisitationProbabilities(self):
        """
        Calculates the probabilities that randomly chosen paths
        pass through nodes. If 5 out of 100 paths (of any length) contain
        node v, it will be assigned a value of 0.05. This measure can be
        interpreted as path-based ground truth for the notion of importance
        captured by PageRank applied to a graphical abstraction of the paths.
        """

        Log.add('Calculating path visitation probabilities...', Severity.INFO)

        # entries capture the probability that a given node is visited on an arbitrary path
        # Note: this is identical to the subpath count of zero-length paths
        # (i.e. the relative frequencies of nodes across all pathways)
        visitation_probabilities = _co.defaultdict(lambda: 0)

        # total number of visits
        visits = 0.0

        for l in self.paths:
            for p in self.paths[l]:
                for v in p:
                    # count occurrences in longest paths only!
                    visitation_probabilities[v] += float(self.paths[l][p][1])
                    visits += float(self.paths[l][p][1])

        for v in visitation_probabilities:
            visitation_probabilities[v] /= visits

        Log.add('finished.', Severity.INFO)

        return visitation_probabilities
