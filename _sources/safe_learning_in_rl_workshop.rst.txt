Safe Learning in RL Workshop Cluster Guide
=================================
For the SRL Workshop, we have provided a docker image that includes the safe-control-gym. This is to prevent the need for manually installing any dependencies as you don't have root access on the cluster. 

To get started, we need to pull the image from docker hub. 

.. code-block:: bash
   module load singularity-ce-3.8.2
   singularity pull docker://roboticsworkshops/srl-workshop

You should see the image being pulled down into the cluster. To check if everything was pulled correctly, you can execute the following command. 

.. code-block:: bash
   singularity instance list 

