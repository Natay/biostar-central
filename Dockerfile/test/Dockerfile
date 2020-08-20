FROM continuumio/miniconda3

# Create the engine environment
COPY engine.yml .
RUN conda env create -f engine.yml

# Execute recipe in engine enviroment.
CMD ["conda", "run", "-n", "engine", "/bin/bash", "-c", "bash $SCRIPT"]



