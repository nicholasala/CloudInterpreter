# CloudInterpreter
Tool for visualize point clouds and verifying classifications found within them with an external classification algorithm. Due to the large size of the point clouds and their high density, the implementation of this tool is not a trivial task. This bachelor thesis project aims to build a **prototype** that allows a fluidly interaction with high-density point clouds and a method for accuracy evaluation of the previus developed classification algorithm.

<p align="center">
  <img src="https://github.com/nicholasala/CloudInterpreter/blob/master/images/lod.png">
</p>

For the creation of this prototype the <a href="https://github.com/intel-isl/Open3D"> **Open3d** </a> library was used through the python API. So most of the code is developed in **python** and a little part in **C++**. The project is mainly composed by two parts:

  * Converter
  * Visualizer

## Converter
To allow a satisfying user experience also with high-density point clouds a Level Of Details (**LOD**) mechanism becomes useful. In order to develop this mechanism, we need a converter that divides the point cloud into a hierarchy of files according to a well-defined logic. The converter developed in python creates an **Octree** based hierarchy of files from an input point cloud. Octree is used to subdivide a three-dimensional environment. In this way a hypothetical visualizer can load only a part of this hierarchy and decrease the computation needed to display the points. The converter accept as second argument the file structure of point cloud that can be:

  * XYZ: spatial coordinates.
  * XYZRGB: spatial coordinates, colour.
  * XYZIRGB: spatial coordinates, intensity, colour.
  * XYZC: XYZ with classification.
  * XYZRGBC: XYZRGB with classification.
  * XYZIRGBC: XYZIRGB with classification.

Example of python code for convert point cloud:

>	    import OctreeFormatTools as oft
>	    gen = oft.Generator("pointcloud.txt", "xyzirgb")
>	    gen.parse()

If the point cloud file contains classfications a dictionary id-name can be passed as third argument:

>	    classes = {
>	        1: "house",
>	        2: "car",
>	       }
>	    gen = oft.Generator("pointcloud.txt", "xyzirgbc", classes)

## Visualizer
A visualizer with LOD mechanism has to do a lot of work. The necessary computation could slow down the application a lot if carried out by a single process. By this consideration and after reading the paper of <a href="https://github.com/SFraissTU/BA_PointCloud"> BA_Pointcloud </a> it was chosen to base the viewer on 3 threads: *loader*, *traversal* and *visualizer*.

<p align="center">
  <img src="https://github.com/nicholasala/CloudInterpreter/blob/master/images/Multithreading.png">
</p>

A visualizer can be started passing the directory of previus generated Octree hierarchy:

>	    import CloudInterpreter
>	    CloudInterpreter.start(octreeDir, 80)

### Loader
The loader process has the task of loading the nodes of the hierarchy previusly presented from hard disk or from LRU cache.

### Traversal
The LOD mechanism is put into effect by traversal. Traversal for each frame calculates which nodes to load and which nodes to remove from the view depending on the position of the camera and the view-frustum.

### Visualizer
The visualizer process has the task of displaying the point cloud composed of all nodes obtained through traversal. For each frame visualizer remove and add points to the render. This thread is the only one that uses Open3D for the cloud render. In order to allow a method for accuracy evaluation of the classifications, a custom Open3D visualizer class has been created. This custom class allows saving a classification id for each point. Additionally through this custom Open3D class a python program can register a callback that return the id of the class of the clicked point.

## Result
The result is a prototype that allow a smooth user experience regardless of the density of the cloud. The prototype allow the identification of the class of a point by clicking this (ctrl + right click). The screenshot below shows the identification of three classes. The classes in the cloud have been inserted randomly, only to verify the functioning of the prototype.

<p align="center">
  <img src="https://github.com/nicholasala/CloudInterpreter/blob/master/images/rilclass.png">
</p>

## Installation
For requirements and installation guide please see <a href="https://github.com/nicholasala/CloudInterpreter/blob/master/README.txt"> README.txt </a>.

## Future developments

* Speed up converter, using multithreading
* Save and read clouds directly in the Open3D format. So avoid converting them before giving them to the viewer.
* Save points and information on the presence of child nodes in separate files
