facescrub
=========

Download dataset from http://vintage.winklerbros.net/facescrub.html

simply rum `python download.py`, all images are downloaded under `download`.

### Notice

Since I want to vertify the image and extract face region from the images, opencv-python package needed. If you are on Windows, this [url](http://www.lfd.uci.edu/~gohlke/pythonlibs/) can be very helpful to install packages.

### What's new in this fork?
Using FirstName_LastName_imageidx_faceidx.jpg as file name as recorded in the txt. Use sha256 value to check if the downloaded image is correct. If not delete it. If certain existing image file doesn't pass its sha256 value check, then delete it and retry to download it.
