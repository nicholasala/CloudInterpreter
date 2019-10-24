FROM ubuntu

#structure passed with --build-arg STRUCTURE="..."
ARG STRUCTURE=none

RUN set -ev

RUN apt-get update
RUN apt-get install -y python3.6
RUN apt-get install -y python3-dev python3-setuptools build-essential python3-pip

RUN apt-get -y install xorg-dev libglu1-mesa-dev libgl1-mesa-glx
RUN apt-get -y install libglew-dev
RUN apt-get -y install libglfw3
RUN apt-get -y install libglfw3-dev
RUN apt-get -y install libjsoncpp-dev
RUN apt-get -y install libeigen3-dev
RUN apt-get -y install libpng-dev
RUN apt-get -y install libjpeg-dev
RUN apt-get -y install python-dev python-tk

ADD src/Main.py src/
ADD src/FrustumManager.py src/
ADD src/CloudInterpreter.py src/
ADD src/OctreeFormatTools.py src/
ADD open3d-0.7.0.0-cp36-cp36m-linux_x86_64.whl /

# Adding point cloud file to docker
ADD example.xyz /

RUN pip3 install --upgrade pip
RUN pip3 install open3d-0.7.0.0-cp36-cp36m-linux_x86_64.whl

CMD ["sh", "-c", "python3 src/Main.py example.xyz $STRUCTURE"]
