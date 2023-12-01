import datetime
import sys
import subprocess
import itertools
import os
import shutil

def update():
    top_level_dir = os.getcwd()
    if not os.path.isdir("builds"):
        os.mkdir("builds")
    if not os.path.isdir("modulefiles"):
        os.mkdir("modulefiles")

    # ICC's cmake modules are broken and stupid so build our own.
    if not os.path.isdir("cmake"):
        cmake_build_script = f"""
mkdir cmake && cd cmake
mkdir install
wget https://github.com/Kitware/CMake/releases/download/v3.26.3/cmake-3.26.3-linux-x86_64.sh
sh cmake-3.26.3-linux-x86_64.sh --skip-license --exclude-subdir --prefix=install
cd ..
        """
        subprocess.run(cmake_build_script, shell=True)

        cmake_modulefile_contents = f"""#%Module1.0

module-whatis {{A cross-platform, open-source build system. CMake is a family of tools designed to build, test and package software. }}

proc ModulesHelp {{ }} {{
    puts stderr {{Name   : cmake}}
    puts stderr {{}}
    puts stderr {{A cross-platform, open-source build system. CMake is a family of tools}}
    puts stderr {{designed to build, test and package software.}}
}}
conflict cmake

prepend-path --delim {{:}} PATH {{{top_level_dir}/cmake/install/bin}}
prepend-path --delim {{:}} ACLOCAL_PATH {{{top_level_dir}/cmake/install/share/aclocal}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{top_level_dir}/cmake/install/.}}

        """

        with open(f"{top_level_dir}/modulefiles/cmake", 'w') as cmake_modulefile:
            cmake_modulefile.write(cmake_modulefile_contents)

    # Only support one compiler/MPI/CUDA combo at a time.
    # This is mostly because only one combo works on ICC at a time...
    compiler_module = "gcc/8.2.0"
    mpi_module = "openmpi/4.1.4-gcc-8.2.0"
    cuda_module = "cuda/10.0"
    cmake_module = f"{top_level_dir}/modulefiles/cmake"
    python_module = "anaconda/3"

    # ICC currently restricts compiling to a certain number of cores
    num_build_cores = 4

    current_datetime = datetime.datetime.now()
    current_datetime = current_datetime.strftime('%Y-%m-%d')

    openmp_options = [True, False]
    cuda_arch_options = [None, 70, 86]
    for openmp_option, cuda_arch_option in itertools.product(openmp_options, cuda_arch_options):
        option_spec_string = f"{'+' if openmp_option else '~'}openmp-cuda-arch-{str(cuda_arch_option)}"
        # Want to build both Debug and Release versions of hpic2deps,
        # but only the Release version of hpic2 itself.
        # First, hpic2deps
        for build_type in ("Debug", "Release"):
            dir_name = f"hpic2deps-{option_spec_string}-{build_type}-{current_datetime}"

            cuda_enabled = cuda_arch_option != None
            # May want to enable Broadwell optimizations, but not sure
            # if that can be used on all of ICC.
            kokkos_cmake_cmd = f"cmake ../kokkos -DKokkos_ENABLE_SERIAL=ON -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_BUILD_TYPE={build_type}"
            if build_type == "Debug":
                kokkos_cmake_cmd += " -DKokkos_ENABLE_DEBUG=ON -DKokkos_ENABLE_DEBUG_BOUNDS_CHECK=ON -DKokkos_ENABLE_DEBUG_DUALVIEW_MODIFY_CHECK=ON"
            if cuda_enabled:
                kokkos_cmake_cmd += f" -DKokkos_ENABLE_CUDA=ON -DKokkos_CUDA_LAMBDA=ON"
                if cuda_arch_option==70 or cuda_arch_option==72:
                    kokkos_cmake_cmd += f" -DKokkos_ARCH_VOLTA{cuda_arch_option}=ON"
                elif cuda_arch_option==80 or cuda_arch_option==86:
                    kokkos_cmake_cmd += f" -DKokkos_ARCH_AMPERE{cuda_arch_option}=ON"
            kokkos_cmake_cmd += f" -DKokkos_ENABLE_OPENMP={'ON' if openmp_option else 'OFF'}"

            mfem_cmake_cmd = f"cmake ../mfem -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_BUILD_TYPE={build_type} -DMETIS_DIR=../../metis-5.1.0/build/Linux-x86_64/install -DHYPRE_DIR=../../hypre_dev/hypre/src/hypre -DMFEM_USE_MPI=YES"
            if cuda_enabled:
                mfem_cmake_cmd += f" -DMFEM_USE_CUDA=YES -DCUDA_ARCH=sm_{cuda_arch_option}"
            elif openmp_option:
                mfem_cmake_cmd += f" -DMFEM_USE_OPENMP=YES"

            build_script = f"""
module purge
module use {top_level_dir}/modulefiles
module load {compiler_module} {mpi_module} {cmake_module} {cuda_module if cuda_enabled else ''}

cd builds
mkdir {dir_name}
cd {dir_name}

# install rust
# set up directories for rust install files
mkdir cargo
mkdir multirust
# setting these env variables installs rust locally,
# rather than in home directory
export CARGO_HOME=$PWD/cargo
export RUSTUP_HOME=$PWD/multirust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $CARGO_HOME/env

# install hypre
# TODO build cuda-aware hypre when cuda enabled
mkdir hypre_dev
cd hypre_dev
git clone git@github.com:hypre-space/hypre.git
cd hypre/src
./configure
make -j{num_build_cores}
make install
cd ../../..

# install spdlog
mkdir spdlog_dev && cd spdlog_dev
git clone git@github.com:gabime/spdlog.git
mkdir build && cd build
cmake ../spdlog -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_BUILD_TYPE={build_type}
make -j{num_build_cores}
make install
cd ../..

# install kokkos
mkdir kokkos_dev && cd kokkos_dev
git clone git@github.com:kokkos/kokkos.git
mkdir build && cd build
{kokkos_cmake_cmd}
make -j{num_build_cores}
make install
cd ../..

# install metis 5
wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz
tar -xvf metis-5.1.0.tar.gz
cd metis-5.1.0
make config prefix=install
make -j{num_build_cores}
make install
cd ..

# install mfem
mkdir mfem_dev && cd mfem_dev
git clone git@github.com:mfem/mfem.git
mkdir build && cd build
{mfem_cmake_cmd}
make -j{num_build_cores}
make install
cd ../..

# install pumimbbl
mkdir pumiMBBL_dev && cd pumiMBBL_dev
git clone git@github.com:SCOREC/pumiMBBL.git
mkdir build && cd build
cmake ../pumiMBBL -DCMAKE_INSTALL_PREFIX=../install -DKokkos_ROOT=../../kokkos_dev/install -DCMAKE_BUILD_TYPE={build_type}
make -j{num_build_cores}
make install
cd ../..

# install rustbca
git clone git@github.com:lcpp-org/RustBCA.git
cd RustBCA
cargo build --release --lib
mkdir include && cd include
ln -s ../RustBCA.h .
cd ..
mkdir lib && cd lib
ln -s ../target/release/liblibRustBCA.so .
cd ../..

# install hdf5
mkdir hdf5_dev && cd hdf5_dev
git clone git@github.com:HDFGroup/hdf5.git
mkdir build && cd build
cmake ../hdf5 -DCMAKE_BUILD_TYPE={build_type} -DHDF5_BUILD_EXAMPLES=OFF -DHDF5_ENABLE_PARALLEL=ON -DHDF5_BUILD_CPP_LIB=ON -DALLOW_UNSUPPORTED=ON -DCMAKE_INSTALL_PREFIX=../install
make -j{num_build_cores}
make install
cd ../..
            """

            subprocess.run(build_script, shell=True)

            build_dir_path = f"{top_level_dir}/builds/{dir_name}"

            # I wrote this modulefile based on the modulefiles generated by
            # spack for each of these packages.
            modulefile_contents = f"""#%Module1.0

module-whatis {{Dependencies for hPIC2 building. }}

proc ModulesHelp {{ }} {{
    puts stderr {{Name   : hpic2deps}}
}}

if {{![info exists ::env(LMOD_VERSION_MAJOR)]}} {{
    module load {mpi_module}
    module load {compiler_module}
    module load {cmake_module}
    module load {python_module}
    {'module load ' + cuda_module if cuda_enabled else ''}
}} else {{
    depends-on {mpi_module}
    depends-on {compiler_module}
    depends-on {cmake_module}
    depends-on {python_module}
    {'depends-on ' + cuda_module if cuda_enabled else ''}
}}
conflict hpic2deps
conflict cmake
conflict gcc
conflict openmpi
conflict cuda

prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_dir_path}/hypre_dev/hypre/src/hypre/.}}
setenv HYPRE_ROOT {{{build_dir_path}/hypre_dev/hypre/src/hypre}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_dir_path}/spdlog_dev/install/.}}
prepend-path --delim {{:}} PATH {{{build_dir_path}/kokkos_dev/install/bin}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_dir_path}/kokkos_dev/install/.}}
setenv KOKKOS_ROOT {{{build_dir_path}/kokkos_dev/install}}
prepend-path --delim {{:}} PATH {{{build_dir_path}/metis-5.1.0/build/Linux-x86_64/install/bin}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_dir_path}/metis-5.1.0/build/Linux-x86_64/install/.}}
setenv METIS_ROOT {{{build_dir_path}/metis-5.1.0/build/Linux-x86_64/install}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_dir_path}/mfem_dev/install/.}}
setenv MFEM_ROOT {{{build_dir_path}/mfem_dev/install}}
setenv PUMIMBBL_ROOT {{{build_dir_path}/pumiMBBL_dev/install}}
setenv RUSTBCA_ROOT {{{build_dir_path}/RustBCA}}
prepend-path --delim {{:}} PATH {{{build_dir_path}/hdf5_dev/install/bin}}
prepend-path --delim {{:}} CMAKE_PREFIX_PATH {{{build_dir_path}/hdf5_dev/install/.}}
append-path --delim {{:}} LD_LIBRARY_PATH {{{build_dir_path}/hdf5_dev/install/lib}}
setenv HDF5_ROOT {{{build_dir_path}/hdf5_dev/install}}

            """

            modulefile_dir = f"{top_level_dir}/modulefiles/hpic2deps/{option_spec_string}/{build_type}"
            if not os.path.exists(modulefile_dir):
                os.makedirs(modulefile_dir)
            with open(f"{modulefile_dir}/{current_datetime}", 'w') as modulefile:
                modulefile.write(modulefile_contents)

if __name__ == "__main__":
    if "update" in sys.argv:
        update()
