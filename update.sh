module load python/3.13.2
(sh -c "python3 campuscluster_update.py update" &> output_update.log) & echo $! > update.pid # Or whichever one is actually working now