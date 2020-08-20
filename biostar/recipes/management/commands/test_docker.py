import docker

import logging

logger = logging.getLogger("engine")


if __name__ == "__main__":
    import os

    working_dir = os.path.join(os.getcwd(), "test_docker")

    # Name of the script relative to working directory.
    script = "script.sh"

    # The prebuilt docker image to run the container in.
    image_name = "testing:latest"

    # Mount current directory as read only
    # working_dir is mounted as write.
    read_mount = os.getcwd()

    # Ensure working dir and script exist.
    os.makedirs(working_dir, exist_ok=True)
    if os.path.isfile(script):
        open(script, "w")

    # Prepare the mounts.
    volumes = {
        # key = Name of path in container
        # value = dict( bind= path to bind on local fs
        #               mode= mount mode (ro,rw, etc)
        read_mount: {'bind': read_mount, 'mode': 'ro'},
        working_dir: {'bind': working_dir, 'mode': 'rw'},

    }

    # Get a client
    client = docker.from_env()

    # Pass along the script name and other env variables.
    stdout = ''
    stderr = ''
    envs = [f"SCRIPT={script}", ]

    # Run the docker container.
    res = client.containers.run(image_name,
                                environment=envs,
                                auto_remove=True,
                                name="testing",
                                volumes=volumes,
                                working_dir=working_dir)

    print(res, "HELLO")
