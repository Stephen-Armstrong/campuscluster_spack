cd ..
module load python/3
git clone -c feature.manyFiles=true https://github.com/spack/spack.git
. spack/share/spack/setup-env.sh
cd -
cp spack_config/* ../spack/etc/spack/.
echo "repos:" > ../spack/etc/spack/repos.yaml
echo "- $PWD/lcpp-spack-repo" >> ../spack/etc/spack/repos.yaml

