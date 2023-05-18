spack install hpic2deps%gcc@7.2.0 ^openmpi@4.1.0%gcc@7.2.0+pmi ^googletest%gcc@7.2.0 ^hypre%gcc@7.2.0 ^spdlog%gcc@7.2.0 ^kokkos%gcc@7.2.0+pic+compiler_warnings+debug+debug_bounds_check+debug_dualview_modify_check ^mfem%gcc@7.2.0~cuda~openmp+debug
spack install hpic2deps%gcc@7.2.0 ^openmpi@4.1.0%gcc@7.2.0+pmi ^googletest%gcc@7.2.0 ^hypre%gcc@7.2.0 ^spdlog%gcc@7.2.0 ^kokkos%gcc@7.2.0+pic+compiler_warnings ^mfem%gcc@7.2.0~cuda~openmp
spack install hpic2deps%gcc@7.2.0 ^openmpi@4.1.0%gcc@7.2.0+pmi ^googletest%gcc@7.2.0 ^hypre%gcc@7.2.0 ^spdlog%gcc@7.2.0 ^kokkos%gcc@7.2.0+pic+compiler_warnings+openmp ^mfem%gcc@7.2.0~cuda+openmp
spack install hpic2deps%gcc@7.2.0 ^openmpi@4.1.0%gcc@7.2.0+pmi ^googletest%gcc@7.2.0 ^hypre%gcc@7.2.0 ^spdlog%gcc@7.2.0 ^kokkos%gcc@7.2.0+pic+compiler_warnings+openmp+debug+debug_bounds_check+debug_dualview_modify_check ^mfem%gcc@7.2.0~cuda+openmp+debug
spack install hpic2deps%gcc@7.2.0 ^openmpi@4.1.0%gcc@7.2.0+pmi ^googletest%gcc@7.2.0 ^hypre%gcc@7.2.0 ^spdlog%gcc@7.2.0 ^kokkos%gcc@7.2.0+pic+compiler_warnings+pthread+debug+debug_bounds_check+debug_dualview_modify_check ^mfem%gcc@7.2.0~cuda~openmp+debug
spack install hpic2deps%gcc@7.2.0 ^openmpi@4.1.0%gcc@7.2.0+pmi ^googletest%gcc@7.2.0 ^hypre%gcc@7.2.0 ^spdlog%gcc@7.2.0 ^kokkos%gcc@7.2.0+pic+compiler_warnings+pthread ^mfem%gcc@7.2.0~cuda~openmp
# As of 5/18/2023, Campus Cluster does not have cusparse so mfem won't work with CUDA.
# As of 5/18/2023, spack has a bug where it can't differentiate between cuda_archs in modulefiles. So just build for cuda_arch=70.
spack install hpic2deps%gcc@7.2.0 ^openmpi@4.1.0%gcc@7.2.0+pmi ^googletest%gcc@7.2.0 ^hypre%gcc@7.2.0 ^spdlog%gcc@7.2.0 ^kokkos%gcc@7.2.0+pic+compiler_warnings+openmp+cuda+cuda_lambda+wrapper cuda_arch=70 ^mfem%gcc@7.2.0~openmp #+cuda cuda_arch=70
spack install hpic2deps%gcc@7.2.0 ^openmpi@4.1.0%gcc@7.2.0+pmi ^googletest%gcc@7.2.0 ^hypre%gcc@7.2.0 ^spdlog%gcc@7.2.0 ^kokkos%gcc@7.2.0+pic+compiler_warnings+openmp+cuda+cuda_lambda+wrapper+debug+debug_bounds_check+debug_dualview_modify_check cuda_arch=70 ^mfem%gcc@7.2.0~openmp+debug #+cuda cuda_arch=70

