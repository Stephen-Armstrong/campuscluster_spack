# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------

from spack import *


class Hpic2deps(BundlePackage):
    """Loads up dependencies for hpic2 so that developers can easily build."""


    homepage = "https://github.com/lcpp-org/hpic2"
    # There is no URL since there is no code to download.


    # notify when the package is updated.
    maintainers = ['logantm2']

    
    version('main')

    depends_on('mpi')
    depends_on('kokkos@:3.8')
    depends_on('spdlog')
    depends_on('hypre')
    depends_on('googletest')
    depends_on('hdf5+cxx+mpi')
    depends_on('mfem~zlib')
    depends_on('metis')
    depends_on('cuda')

    # There is no need for install() since there is no code.
