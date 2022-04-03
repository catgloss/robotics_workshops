Safe Learning in RL Workshop Cluster Guide
=================================
For the SRL Workshop, we have provided a docker image that includes the safe-control-gym. This is to prevent the need for manually installing any dependencies as you don't have root access on the cluster. 

On the cluster, we use `singularity <https://sylabs.io/guides/2.6/user-guide/index.html>`_ to manage and work with docker images. Refer to the link for additional documentation. To get started, we need to pull the image from docker hub. 

.. code-block:: bash
   module load singularity-ce-3.8.2
   singularity pull docker://roboticsworkshops/srl-workshop:env_image

You should see the image being pulled down into the cluster. You should now see a .sif file in your current working directory call srl-workshop_env_image.sif. 

To use this image, you must use SLURM to run an interactive job or a job in the background. 

Interactive Session w/ Singularity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to just explore the safe-control-gym or want to debug some code, it is best to run an interactive job. To get started, schedule an interactive job with srun 

.. code-block:: bash 
   srun -c 4 --gres=gpu:1 --mem=32GB --qos=nopreemption -p interactive --pty bash

You should now see that you are running on the node for the job. 

Now, you can run singularity exec on your image to start a session in the image. 

.. code-block:: bash 

   singularity shell --nv -B /path/to/your/cwd:/root srl-workshop_env_image bash

This will open up an interactive command line session with the image and you will be able to directly run any of code in the safe-control-gym through this image. Note that if you will have to use vim to interact with files while in this interactive session. 

Non-interactive Session w/ Singularity 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't need to be able to look at source files and just want to run a job on the cluster, you can use either srun and execute the your commands with `singularity exec` or run a background job with sbatch and include your commands in the job script. 

Option 1: srun and singularity exec 

.. code-block:: bash 

   srun -c 4 --gres=gpu:1 --mem=32GB --qos=nopreemption -p interactive --pty bash
   singularity exec --nv -B /path/to/your/cwd:/root srl-workshop_env_image bash -c "<your command(s)>" 

This will execute your commands in the image with starting a shell session. 

Option 2: sbatch and job script 

Your job.sh will look something like this

.. code-block:: bash 

   #!/bin/bash
   #SBATCH --ntasks=1
   #SBATCH --mem=24G
   #SBATCH -c 8
   #SBATCH --partition=t4v2
   #SBATCH --export=ALL
   #SBATCH --output=%x.%j.log
   #SBATCH --gres=gpu:1

   hostname
   nvidia-smi

   module load cuda-11.0
   module load singularity-ce-3.8.2

   singularity exec --nv -B /path/to/your/cwd:/root \
                       bash -c \
                       "<your command>"

Submit the job as usual: 

.. code-block:: bash

   sbatch job.sh

Refer to the tutorial and README in the safe-control-gym to learn more about configuring and running experiments. 
   
   






