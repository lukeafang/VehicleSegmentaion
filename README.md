# VehicleSegmentaion

Segment vehicles and count the numver of vehicles from input video.

## Getting Started

### Prerequisites

Python 3.x, opencv, numpy

### Installing

You can install package "opencv" and "numpy" via pip install

```
pip install numpy
```
```
pip install opencv-python
```

or run virtual environment by the copy of the project.

In the project folder,
Enter virtual environment
```
source venv/bin/activate
```

Leave virtual environment
```
deactivate
```

### Running the project

There are several input parameters when run the project

Background update mode:

mode1: use motion information to update background
```
python main.py mode1
```
or

mode2: use detected object to update background
```
python main.py mode2
```

File Path:
-p [file_path], Path of input video
```
python main.py mode2 -p data/T1.mp4
```

#### Optional parameters

Update rate of pixels:
-u [1-10], updateRatio of pixels in background Image, 10 => 100% update
```
python main.py mode2 -p data/T1.mp4 -u 10
```

Update frequence of background:

-uc [n>0], update frequence of background Image

ex: update background every 2 frame.
```
python main.py mode2 -p data/T1.mp4 -uc 2
```


Scale image:
-s [1/0], 1 => true, scale image 
```
python main.py mode2 -p data/T1.mp4 -s 1
```

### Terminate the program  

Press 'q' to leave the program.

Press 's' to save the image of current frame in the output folder.



