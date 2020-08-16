FROM continuumio/miniconda3

# Create the engine environment
COPY engine.yml .
RUN conda env create -f engine.yml

# TODO : NEEDS AN INSTALLATION / INIT SCRIPT INCASE WE NEED TO GET MORE DEPENDACNIES IN.

# Create the qiime2 environment

# Execute recipe in engine enviroment.
CMD ["conda", "run", "-n", "engine", "/bin/bash", "-c", "bash $SCRIPT>$STDOUT 2>$STDERR"]

