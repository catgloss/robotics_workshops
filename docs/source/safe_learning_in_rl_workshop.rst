Safe Learning in RL Workshop Cluster Guide
=================================
`Wav2Veq-U <https://github.com/pytorch/fairseq/tree/main/examples/wav2vec/unsupervised>`__
is a model provided inside the the `Fairseq <https://github.com/pytorch/fairseq>`__ toolkit
that makes speech recognition possible by using unpaired audio and text
data, hence called unsupervised. This tutorial is a complementary set of instructions in addition to the
original
`README <https://github.com/pytorch/fairseq/tree/main/examples/wav2vec/unsupervised#readme>`__ of the Wav2Vec-U project.


The main steps in running the Wav2Veq-U model are as follows: 

* Preparation of speech representations and text data  
* Generative adversarial (GAN) training 
* Decoding using Viterbi or Kaldi decoders
* Iterative self-training + Kaldi LM-decoding

1. Environment Setup
-----------------------

Running the Wav2Veq-U project requires installing multiple dependencies.
The list of the dependencies are as follows:

* `RVadfast <https://github.com/zhenghuatan/rVADfast>`__
* `KenLM <https://github.com/kpu/kenlm>`__  
* `Intel MKL <https://www.intel.com/content/www/us/en/develop/documentation/get-started-with-mkl-for-dpcpp/top.html>`__
* `PyKaldi <https://github.com/pykaldi/pykaldi>`__
* `Flashlight Python binding <https://github.com/flashlight/flashlight>`__ 
* `Fairseq toolkit <https://github.com/pytorch/fairseq>`__

In addition to the above-mentioned requirements, a comprehensive list of
required Python packages can be found in
`requirements.txt <https://github.com/VectorInstitute/ASR/blob/main/unsupervised_asr/requirements.txt>`__.
(The project has been tested on ``python = 3.6.9``.)

In order to simplify the process of installing dependencies we have
provided a `Dockerfile <https://github.com/VectorInstitute/ASR/blob/main/unsupervised_asr/Dockerfile>`__ to build the unsupervised Docker image.
The image can be found on `Docker Hub <https://hub.docker.com/r/convaiasr/unsupervised>`__.

Depending on where and how want to run the project, there are different
approaches towards installing the dependencies. Here, we consider three
cases. 

**1. Running the project on a machine where you have root access and can install all the packages directly**

  * In this case you can follow the same steps as described in the `Dockerfile <https://github.com/VectorInstitute/ASR/blob/main/unsupervised_asr/Dockerfile>`__ to make sure that you have all the packages installed and the required environment variables are set. In the Dockerfile, after installing the system requirements and Python packages, the dependencies are installed in the same order as mentioned above. 

  * Note that due to some discrepancies, some changes has been made to the Fairseq repository. It is recommended that you use the fork of Fairseq repository `here <https://github.com/mahshidaln/fairseq>`__, similar to the what has been done in the Dockerfile.

**2. Running the project inside a Docker container**

  * In this case you can pull the Docker image using the following command.

   .. code-block:: bash

       docker pull convaiasr/unsupervised

**3. Running the project on Vector cluster inside a Singularity Container**
  * In this case you can use Singularity to pull the Docker image. 

   .. code-block:: bash

        # loading singularity
        module load singularity-ce-3.8.2
        # pulling the image
        singularity pull docker://convaiasr/unsupervised

1.1 Running Scripts on Your System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* If you are running the project on your own system directly, you can run the exact scripts mentioned in Training Guide and Inference Guide.

* If you are running the project inside the Docker container, you can run the container to have an interactive bash session and then run the commands while binding directories on the host system to save the results files. 

    .. code-block:: bash

        docker run -v /on/my/host/1:/on/the/container/1 \
                   -v /on/my/host/2:/on/the/container/2 \
                   unsupervised /bin/bash

1.2 Running Scripts On Vector Cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* In order to run the project on the Vector cluster using singularity you need to submit a job on SLURM scheduler. To do so, you need to create a shell script (e.g. ``job.sh``) and submit the job.

    .. code-block:: bash

        sbatch job.sh  
              
* Below is a sample of the job script that runs Singularity on Vector cluster for training and inference step. You can use the following sample and replace the command string following -c with the actual commands that are required for every step of data preprocessing by binding the appropriate directories. 

 We have already trained the GAN on LibriSpeech dataset. We used 100 hours of audio data and we used 10% of the LibriSpeech language model corpus as the text data. The preprocessed data and the checkpoints can be found on the Vector cluster directory ``/ssd03/projects/convai/asr/``.

 The checkpoints to the trained GAN model can be found in ``/ssd03/projects/convai/asr/gan_checkpoints`` while preprocessed text and audio data are stored in ``/ssd03/projects/convai/asr/librispeech_preprocessed``

 You can keep the config (.yaml) files for training and inference on the host system and edit them directly or pass the required config options as arguments in the following script. 
 The sample config files can be found `here <https://github.com/VectorInstitute/ASR/blob/main/unsupervised_asr/config>`__. (It is assumed that the data directory ``/ssd03/projects/convai/asr/`` from the host is binded to ``/unsupervised/data`` inside the container)

 
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

        singularity exec --nv -B /path/to/data/dir:/unsupervised/data \
                            -B /path/to/config/dir:/unsupervised/config \
                            -B /path/to/outputs/dir:/unsupervised/outputs unsupervised_latest.sif \
                            bash -c \
                            "cd /fairseq/examples/wav2vec/unsupervised && \
                            PYTHONPATH=/fairseq PREFIX=w2v_unsup_gan_xp fairseq-hydra-train \
                            -m --config-dir config/gan \ # or /unsupervised/config/gan if config files are on the host system
                            --config-name w2vu \
                            hydra.output_subdir=/unsupervised/outputs \
                            hydra.run.dir=/unsupervised/outputs \
                            hydra.sweep.dir=/unsupervised/outputs \
                            task.data=/path/to/features/precompute_unfiltered_pca512_cls128_mean_pooled \
                            task.text_data=/path/to/data/phones \
                            task.kenlm_path=/path/to/data/phones/kenlm.phn.o4.bin \
                            common.user_dir=/fairseq/examples/wav2vec/unsupervised \
                            common.seed=0"
    

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
        
        singularity exec --nv -B /path/to/data/dir:/unsupervised/data \
                            -B /path/to/config/dir:/unsupervised/config \
                            -B /path/to/outputs/dir:/unsupervised/outputs unsupervised_latest.sif \
                            bash -c \
                            "cd /fairseq/examples/wav2vec/unsupervised && \
                            python w2vu_generate.py --config-dir config/generate --config-name kaldi_wrd \ #or /unsupervised/config/generate if config files are on the host system
                            hydra.output_subdir=/unsupervised/outputs \ 
                            hydra.run.dir=/unsupervised/outputs \
                            hydra.sweep.dir=/unsupervised/outputs \
                            fairseq.common.user_dir=/fairseq/examples/wav2vec/unsupervised \
                            fairseq.task.data=/path/to/features/precompute_unfiltered_pca512_cls128_mean \
                            fairseq.common_eval.path=/path/to/gan/checkpoint.pt \
                            results_path=/where/to/save/transcriptions \
                            kaldi_decoder_config.hlg_graph_path=path_to/HLG \
                            kaldi_decoder_config.output_dict=path_to/kaldi_dict"                           

* Throughout the tutorial there are multiple references to some environment variables such as $FAIRSEQ_ROOT, $KENLM_ROOT, $RVAD_ROOT. These values need to be replaced with the paths set inside the container which are as follows. 

    .. code-block:: bash

        FAIRSEQ_ROOT=/fairseq
        KENLM_ROOT=/opt/kenlm
        RVAD_ROOT=/opt/rVADfast
        KALDI_ROOT=/opt/pykaldi/tools/kaldi
        FASTTEXT=/opt/fasttext

* Also set all other paths to input/output files/directories with respect to the binding that you set for the container.
    
* If you wish to make changes to the source code you might want to keep a clone of the fairseq repository on the host system and bind the unsupervised project directory to its corresponding location inside the container.

    .. code-block:: bash

        singularity exec -B /path/to/host/fairseq/examples/wav2vec/unsupervised:/fairseq/examples/wav2vec/unsupervised ...



2. Training Guide
---------------

Tha main training step in this project is to train a GAN model on unpaired audio and text. But before that, both audio and text data need to be preprocessed. 

Here we elaborate on LibriSpeech preprocessing. You can also find instructions on `TIMIT <https://catalog.ldc.upenn.edu/LDC93s1>`__ preprocessing in the original `README <https://github.com/pytorch/fairseq/tree/main/examples/wav2vec/unsupervised#readme>`__.

2.1 Audio preprocessing (LibriSpeech)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Audio preprocessing starts with splitting the dataset, creating a manifest file, detecting silent segments and removing them using rVAD. 
    .. code-block:: bash

        # create a manifest file for the set original of audio files
        python $FAIRSEQ_ROOT/examples/wav2vec/wav2vec_manifest.py /dir/to/save/audio/files --ext wav --dest /path/to/new/train.tsv --valid-percent 0

        python scripts/vads.py -r $RVAD_ROOT < /path/to/train.tsv > train.vads

        python scripts/remove_silence.py --tsv /path/to/train.tsv --vads train.vads --out /dir/to/save/audio/files

        python $FAIRSEQ_ROOT/examples/wav2vec/wav2vec_manifest.py /dir/to/save/audio/files --ext wav --dest /path/to/new/train.tsv --valid-percent 0.01

Note that the silence removal should also be applied to the test set before the prepare_audio script is called. (The original silence removal scripts only consider train and valid sets)

The next steps are about capturing the audio representations using the wav2veq 2.0 model, applying PCA, detecting the segments using k-means clustering and applying mean pooling. All these steps are followed in the ``prepare_audio.sh``.

    .. code-block:: bash

        zsh scripts/prepare_audio.sh /dir/with/{train,test,valid}.tsv /output/dir /path/to/wav2vec2/model.pt 512 14

Note that if you have splits different than train/valid/test, you will need to modify this script. The last two arguments are the PCA dimensionality and the 0-based index of the layer from which to extract representations.

The major steps in the script are as follows:

1. Extracting audio representation using Wav2Vec 2.0 (the pretrained models can be found on the `github page <https://github.com/pytorch/fairseq/tree/main/examples/wav2vec#pre-trained-models>`__). 

  * Note that you need to download a checkpoint that has not been finetuned e.g. Wav2Vec 2.0 Large (LV-60).

2. Training the clustering model on the train set.
3. Applying the clustering to all audio subsets.
4. Training PCA on the train set.
5. Applying PCA on all the audio subsets.
6. Calculating the means of the PCA results.
7. Applying mean pooling.

The .wrd, .ltr, .phn files also need to be generated for the data splits (train, valid, test) since they are used in evaluation and error rate calculation. 

- The .wrd files includes the real transcription of audio files in the order the are manifested in the {train, valid, test}.tsv after removing silence (the manifest script reorders the files). 

- The .ltr files can be achieved using wrd_to_ltr.py:

    .. code-block:: bash

        python $FAIRSEQ_ROOT/examples/wav2vec/unsupervised/scripts/wrd_to_ltr.py --compact < $target_dir/${split}.wrd > $target_dir/${split}.ltr

- The .phn files can be generated using a phonemizer. (for English language G2P is the recommended phonemizer):

    .. code-block:: bash

        python $FAIRSEQ_ROOT/examples/wav2vec/unsupervised/scripts/g2p_wrd_to_phn.py --compact < $target_dir/${split}.wrd > $target_dir/${split}.phn 
    

2.2 Text preprocessing (LibriSpeech)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Text preprocessing is done through the ``prepare_text.sh`` script:

    .. code-block:: bash

        zsh scripts/prepare_text.sh language /path/to/text/file /output/dir 1000 g2p /path/to/fasttext/lid/model


The stpes in the script are as follows:

1. Normalizing and filtering text by removing numbers, punctuations, and words from other languages.

  * The sixth argument is the path to pre-trained fasttext LID models that can be downloaded `here <https://fasttext.cc/docs/en/language-identification.html>`__.

2. Fairseq preprocessing to generate the dict.txt file for words.
3. Applying the phonemizer and generating the phone.txt.

  * The fifth argument is which phonemizer to use. Supported values are `espeak <http://espeak.sourceforge.net/>`__, `espeak-ng <https://github.com/espeak-ng/espeak-ng>`__, and `G2P <https://github.com/Kyubyong/g2p>`__ (english only).

4. Generating lexicon.lst.
5. Fairseq processing on the phonemes to filter the phonemes that are seen less than a threshold and generate phones/dict.txt.

  * The threshold is set by the the fourth argument i.e. the minimum number observations of phones to keep. If your text corpus is small, you might want to reduce this number

6. Generating the filtered lexicon according to the phonemes dictionary.
7. Inserting <SIL> into the phone transcription and generate lm.phones.filtered.txt.
8. Adding SIL to the phone dictionary.
9. Fairseq preprocessing using the updated phone dictionary.
10. Generating a 4-gram word lamguage model using kenlm and generating arpa and bin files.
11. Creating a fst decoding model using Kaldi. (The outputs will be used for word decoding).
12. Generating a 4-gram phoneme language model using kenlm and generating arpa and bin files.
13. Creating a fst decoding model using Kaldi. (The outputs will be used for phoneme decoding).

2.3 GAN Training
~~~~~~~~~~~~

After the unpaired text and audio representations are prepared, they are used to to train the GAN model. The configuration file for GAN training can be found in the ``config/gan`` directory.  

Launching GAN training on top of preprocessed features, with default hyperparameters can be done with:

    .. code-block:: bash

        PREFIX=w2v_unsup_gan_xp
        TASK_DATA=/path/to/features/precompute_unfiltered_pca512_cls128_mean_pooled  
        TEXT_DATA=/path/to/data/phones  # path to fairseq-preprocessed GAN data (phones dir)
        KENLM_PATH=/path/to/data/phones/kenlm.phn.o4.bin  # KenLM 4-gram phoneme language model (LM data = GAN data here)

        PYTHONPATH=$FAIRSEQ_ROOT PREFIX=$PREFIX fairseq-hydra-train \
            -m --config-dir config/gan \
            --config-name w2vu \
            task.data=${TASK_DATA} \
            task.text_data=${TEXT_DATA} \
            task.kenlm_path=${KENLM_PATH} \
            common.user_dir=${FAIRSEQ_ROOT}/examples/wav2vec/unsupervised \
            model.code_penalty=2 or 4 \
            model.gradient_penalty=1.5 or 2.0 \
            model.smoothness_weight=0.5 or 0.75 or 1.0 \
            common.seed=range(0,5)


3. Inference Guide
----------------

Once we find the best checkpoint (chosen using unsupervised metric that combined language model perplexity and vocabulary usage), we can use it to generate phone labels (or word labels with an appropriate Kaldi decoder):

    .. code-block:: bash

        python w2vu_generate.py --config-dir config/generate --config-name viterbi \
        fairseq.common.user_dir=${FAIRSEQ_ROOT}/examples/wav2vec/unsupervised \
        fairseq.task.data=/path/to/dir/with/features \
        fairseq.common_eval.path=/path/to/gan/checkpoint \ 
        fairseq.dataset.gen_subset=valid results_path=/where/to/save/transcriptions


- Decoding can be done either without a language model (e.g. Viterbi decoding) or with a language model (Kaldi Decoding). Decoding without a LM works best on the same adjacent-mean-pooled features that the gan was trained on, while decoding with LM works better on features before the adjacent time-step mean-pooling step (without the "_pooled" suffix).

- The config for Viterbi decoding to generate phone labels can be found in ``config/generate/viterbi.yaml``.

- Kaldi decoder can be applied before and after self-training for phoneme and word decoding. The full list of Config parameters can be found in the w2lu.generate.py. When you want to use the Kaldi decoder, you should make sure that Kaldi decoder config are included in the config file. You can find out more about the config in kaldi_decoder.py and kaldi_initializer.py. There two necessary config items:

    .. code-block:: bash

        hlg_graph_path: path_to/HLG.phn.kenlm.wrd.o40003.fst (for word decoding) or path to HLG.phn.lm.phones.filtered.06.fst (for phoneme decoding)
        output_dict: path_to/kaldi_dict.kenlm.wrd.o40003.txt or path_to/kaldi_dict.lm.phones.filtered.06.txt 

- The config for Kaldi decoding to generate phone labels can be found in ``config/generate/kaldi_phn.yaml``
- The config for Kaldi decoding to generate phone labels can be found in ``config/generate/kaldi_wrd.yaml``
- Note that the targets argument indicates if the output are supposed to be phonemes or words and in case of phonemes (phn) the WER is actually the PER.
- Note that during inference the dict.phn.txt should be present in the audio features directory. 

4. Iterative self-training + Kaldi LM-decoding
-------------------------------------------
For self-training you can refer to the original `README <https://github.com/pytorch/fairseq/tree/main/examples/wav2vec/unsupervised#readme>`__.

Further instructions will be added soon.


5. Applied Changes
---------------
A few changes were made to the forked version of the repository to prevent errors:

- ``capture_output`` is removed from python subprocess so the ``kaldi_init.py`` of fairseq needed to be updated. (replaced with ``std_out = PIPE`` and ``std_err = PIPE`` where necessary)
- Kaldi logging in ``add-self-loop-simple.cc`` was removed.
- According to latest updates of fairseq the optimization ``amsgrad`` option caused errors and was removed from the training config file.

