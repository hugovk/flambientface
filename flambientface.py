#!/usr/bin/python
"""
Hacked to triangulize your face

This program is demonstration for face and object detection using haar-like features.
The program finds faces in a camera image or video stream and displays a red box around them.

Original C implementation by:  ?
Python implementation by: Roman Stanchak, James Bowman
"""
import sys
import cv2.cv as cv
from optparse import OptionParser
import os
import shutil

try:
    import triangulizor
except ImportError:
        sys.exit('Could not import Triangulizor (do `pip install triangulizor`')

try:
    import Image
except ImportError:
    try:
        import PIL.Image as Image
    except ImportError:
        sys.exit('Could not import Python Imaging Library')

try: import timing # Optional, http://stackoverflow.com/a/1557906/724176
except: None

# Parameters for haar detection
# From the API:
# The default parameters (scale_factor=2, min_neighbors=3, flags=0) are tuned 
# for accurate yet slow object detection. For a faster operation on real video 
# images the settings are: 
# scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING, 
# min_size=<minimum possible face size

min_size = (20, 20)
image_scale = 2
haar_scale = 1.2
min_neighbors = 2
# haar_flags = 0 # to detect all objects
haar_flags = cv.CV_HAAR_FIND_BIGGEST_OBJECT # to detect only one

WINDOW_NAME = "flambient"
TEMP_DIR = "flambient_temp"
TEMP_BASE = "flambient_temp_"
TEMP_SUFFIX = ".png"

count = 0

def opencv_to_pil(opencv_img):
    return Image.fromstring("RGB", cv.GetSize(opencv_img), opencv_img.tostring())

def create_temp_dir():
    if os.path.isdir(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    if not os.path.isdir(TEMP_DIR):
        os.mkdir(TEMP_DIR)

def remove_temp_dir():
    print "Deleting temp directory"
    shutil.rmtree(TEMP_DIR)

def start_timer():
    return cv.GetTickCount()

def stop_timer(t, message):
    t = cv.GetTickCount() - t
    print message + "\t= %gms" % (t/(cv.GetTickFrequency()*1000.))

def detect_and_draw(img, cascade):
    global count
    # allocate temporary images
    gray = cv.CreateImage((img.width,img.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(img.width / image_scale),
    		       cv.Round (img.height / image_scale)), 8, 1)

    # convert color input image to grayscale
    cv.CvtColor(img, gray, cv.CV_BGR2GRAY)

    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

    cv.EqualizeHist(small_img, small_img)

    if(cascade):
        t = start_timer()
        faces = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors, haar_flags, min_size)
        stop_timer(t, "detection time")
        if faces:
            for ((x, y, w, h), n) in faces:
                print "Found"
                t0 = start_timer()
                # the input to cv.HaarDetectObjects was resized, so scale the 
                # bounding box of each face and convert it to two CvPoints
                w = int(w * image_scale)
                h = int(h * image_scale)
                x = int(x * image_scale)
                y = int(y * image_scale)
                
                cropped = cv.CreateImage((w, h), img.depth, img.nChannels)
                src_region = cv.GetSubRect(img, (x, y, w, h))
                cv.Copy(src_region, cropped)
                stop_timer(t, "crop time")

                # OpenCV to PIL
                t = start_timer()
                pil_image = opencv_to_pil(cropped)
                stop_timer(t, "OpenCV to PIL")

                # Triangulize!
                t = start_timer()
                pil_image = triangulizor.triangulize(pil_image, options.tile_size)
                stop_timer(t, "triangulize")

                # PIL to OpenCV
                t = start_timer()
                cropped = cv.CreateImageHeader(pil_image.size, cv.IPL_DEPTH_8U, 3) # depth, channels
                cv.SetData(cropped, pil_image.tostring())
                stop_timer(t, "PIL to OpenCV")

                # Paste triangulized image back in
                t = start_timer()
                cv.SetImageROI(img, (x, y, cropped.width, cropped.height))
                cv.Copy(cropped, img)
                cv.SetImageROI(img, (0, 0, img.width, img.height))
                stop_timer(t, "paste time")

                # cv.Rectangle(img, (x, y), (x + w, y + h), cv.RGB(255, 0, 0), 3, 8, 0)
                stop_timer(t0, "process time")

    cv.ShowImage(WINDOW_NAME, img)
    if options.outfile:
        t = start_timer()
        outfile = os.path.join(TEMP_DIR, TEMP_BASE + str(count).zfill(6) + TEMP_SUFFIX)
        cv.SaveImage(outfile, img)
        stop_timer(t, "save time")
        count += 1

if __name__ == '__main__':

    parser = OptionParser(usage = "usage: %prog [options] [filename|camera_index (hint: try 1)]")
    parser.add_option("-c", "--cascade", action="store", dest="cascade", type="str", help="Haar cascade file, default %default", default = "D:\\temp\\opencv\\data\\haarcascades\\haarcascade_frontalface_alt.xml")
    parser.add_option("-t", "--tile-size", type=int, default=30, help='Tile size (should be divisible by 2. Use 0 to guess based on image size).') # 0 is to guess
    parser.add_option("-o", "--outfile", help='Output filename of animated gif')
    (options, args) = parser.parse_args()

    cascade = cv.Load(options.cascade)
    
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    input_name = args[0]
    if input_name.isdigit():
        capture = cv.CreateCameraCapture(int(input_name))
    else:
        capture = None

    cv.NamedWindow(WINDOW_NAME, 1)

    if capture:
        frame_copy = None
        frames = []
        if options.outfile:
            create_temp_dir()
        
        while True:
            frame = cv.QueryFrame(capture)
            if not frame:
                cv.WaitKey(0)
                break
            if not frame_copy:
                frame_copy = cv.CreateImage((frame.width,frame.height),
                                            cv.IPL_DEPTH_8U, frame.nChannels)
            if frame.origin == cv.IPL_ORIGIN_TL:
                cv.Copy(frame, frame_copy)
            else:
                cv.Flip(frame, frame_copy, 0)
            
            detect_and_draw(frame_copy, cascade)

            if cv.WaitKey(10) >= 0:
                break
        
        cv.DestroyWindow(WINDOW_NAME)
        
        if options.outfile:
            t = start_timer()
            print "Create animated gif"
            inspec = os.path.join(TEMP_DIR, TEMP_BASE + "*" + TEMP_SUFFIX)
            cmd = "convert -delay 20 -loop 1 " + inspec + " " + options.outfile
            print cmd
            os.system(cmd)
            stop_timer(t, "create time")
            remove_temp_dir()
        
    else:
        image = cv.LoadImage(input_name, 1)
        detect_and_draw(image, cascade)
        cv.WaitKey(0)
        cv.DestroyWindow(WINDOW_NAME)
