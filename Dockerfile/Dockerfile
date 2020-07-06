FROM continuumio/miniconda3

# Create the engine environment
COPY engine.yml .
RUN conda env create -f engine.yml


# Create the qiime2 environment


# Execute recipe in engine enviroment.
CMD ["conda", "run", "-n", "engine", "/bin/bash", "-c", "bash $(echo $FOO)"]




