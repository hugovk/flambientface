flambientface
=============

Quick hack to flambient a face from webcam or file

Requirements
---

 *  OpenCV,  
 * PIL, 
 * Triangulizor (do `pip install triangulizor`)
 
Usage
---
You may need to edit the default cascade location, or use -c to point to it.

```
Usage: flambientface.py [options] [filename|camera_index (hint: try 1)]

Options:
  -h, --help            show this help message and exit
  -c CASCADE, --cascade=CASCADE
                        Haar cascade file, default D:\temp\opencv\data\haarcas
                        cades\haarcascade_frontalface_alt.xml
  -t TILE_SIZE, --tile-size=TILE_SIZE
                        Tile size (should be divisible by 2. Use 0 to guess
                        based on image size).
```

Examples
---

Run on a file:

```flambientface.py filename.jpg ```

Run on a webcam:

```flambientface.py 1 ```

Run on a webcam with tile size 12:

```flambientface.py 1 --tile_size 12```

Run on a webcam and guess the tile size:

```flambientface.py 1 --tile-size 0```

Run on a webcam and detect noses:

```flambientface.py 1 -c \temp\opencv\data\haarcascades\haarcascade_mcs_nose.xml```

