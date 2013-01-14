iTunes U Course Manager Tools
=============================

Tools for automating batch processes in iTunes U Course Manager.

* Author: John Dyer [http://j.hn/]
* School: Dallas Theological Seminary [http://www.dts.edu/]
* License (MIT): [http://creativecommons.org/licenses/MIT/]

Requirements
------------

* Python 2.7
* requests library [http://python-requests.org]

Scripts
=======

itunes-batchupload.py
---------------------
It's quite time consuming to upload multiple files to iTunes U Course Manager, so this script can automatically upload an entire folder of files into the course 'Materials' on iTunes U.

`python itunesu-batchupload.py -u username@domain.edu -p ******* -c MATH500 -i 'Math500/video'`

* `-u` Your Apple ID
* `-u` Your Apple ID password
* `-c` Course short code
* `-i` Path to files 


itunes-createposts.py
---------------------
Once the files are uploaed, this script attempts to create 'Posts' which list all the videos for 'Topic' in an iTunes U outline. The detection routine is specific to DTS's naming convention, but it should be adaptable to others.

`python itunesu-createposts.py -u username@domain.edu -p ******* -c MATH500`

* `-u` Your Apple ID
* `-u` Your Apple ID password
* `-c` Course short code