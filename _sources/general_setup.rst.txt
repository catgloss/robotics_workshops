
*********************************************
Working on the Vector Cluster (General Guide)
*********************************************


This guide provides the general process for getting access to and running jobs on the vector cluster.


Getting Access
-----------------------

An account on the cluster has already been made for you. You will just need to be able to login to get started.

Step 1: Logging In
^^^^^^^^^^^^^^^^^^

You will receive an email from Vector with your credentials for logging into the cluster. The cluster is accessed using ssh so you can directly use the Linux/MacOS terminal or Powershell for Windows. If you want to have a more accessible environment, using an IDE like VS code is recommended. A quick guide for setting up VS code can be found `here <https://catgloss.github.io/robotics_workshops/general_setup.html#optional-vs-code-setup>`_ 

Which ever method use choose from the above to login, the process is the same. First, ssh in.

.. code-block:: bash
   
   ssh <your username>@x.vectorinstitute.ai 
 
You will be prompted for your password. Enter your password (provided in the email). 
 
Step 2: Setting up MFA
^^^^^^^^^^^^^^^^^^ 

After entering your password (correctly), you will be provided a link to enroll in DUO multi-factor authentication. 

Install the DUO app on your iOS or Android device and scan the QR code given through the link to complete sign up. 

When you login again, you can choose to get an SMS notif or directly get a passcode through the DUO app. You can also optionally setup the `Vector VPN <https://catgloss.github.io/robotics_workshops/general_setup.html#optional-vs-code-setup>`_.

Step 3: Changing your password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you've successfully accessed the cluster after setting up DUO, you will need to change your password. 

Enter the following command: 

.. code-block:: bash
   
   passwd

Change your password to something secure. 

Step 4: Finishing Setup 
^^^^^^^^^^^^^^^^^^^^^^^

You are automatically in your profile's home directory. If you ever need to check which directory you are in, you can run the following command

.. code-block:: bash
   
   pwd

and your current directory will be spit out

Working on the Cluster 
----------------------

For the purposes of these workshops, we have simplified the computing guide provided through `Vector <https://support.vectorinstitute.ai/Computing>`_ (which you will have access to once your account is setup). 

The basic method for running a job is as follows: 

(Optional) Vector VPN
---------------------

This is how to setup the Vector VPN 

(Optional) VS Code Setup 
-------------------------

Here is how to setup VS Code for working remotely on the cluster 
