#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
iTunes U Course Manager Batch Upload Script

Author: John Dyer <http://j.hn/> @johndyer
Company: Dallas Theological Seminary <http://www.dts.edu/> @dallasseminary
Dependencies: Python 2.7, requests

USAGE:
$ python itunesu.py -u USERNAME -p PASSWORD -c COURSESHORTNAME -i PATHTOFILES
python itunesu.py -u social@dts.edu -p ******* -c ST106 -i '/Volumes/icedtea/Av/Online/Online Amazon/dtsoe/st106'

License (MIT): http://creativecommons.org/licenses/MIT/
"""

import requests
import sys
import getopt
import json
import os

# get variables

def main(argv):  
	
	username = ''
	password = ''
	courseid = ''
	path = ''
	
	opts, args = getopt.getopt(argv, 'u:p:c:i:')
	
	# PARSE command line
	for opt, arg in opts:                
		if opt in ("-u"):      
			username = arg
		elif opt in ("-p"):
			password = arg
		elif opt in ("-c"):
			courseid = arg
		elif opt in ("-i"):
			path = arg
			
	if username == '' or password == '':
		print 'Missing username (-u) or password (-p)'
		sys.exit(1)
	if courseid == '':
		print 'Missing course shortname (-c)'
		sys.exit(1)
	if path == '':
		print 'Missing input directory (-i)'
		sys.exit(1)		
	
	# LOGIN
	s = requests.session()
	print "Logging in with " + username 
	payload = {'enteredUsername':username,'password':password}
	login_request = s.post("https://itunesu.itunes.apple.com/WebObjects/LZDirectory.woa/ra/login", data=payload, verify=False)
	login_data = login_request.text.strip()
	
	if login_data == 'unauthorized':
		print '-Error logging in'
		sys.exit(1)
		
	logged_in_user_id = str(login_request.json()[u'personId'])	
		
		
	# WAKE to get correct URL for posting
	wake_data = s.get('https://itunesu.itunes.apple.com/WebObjects/LZDirectory.woa/ra/wake/')
	pod_host = str(wake_data.json()[u'podHost'])
		
	# FIND course in List
	print "Getting list of courses"

	courses_url = pod_host + '/WebObjects/LZTeacher.woa/ra/teachers/' + logged_in_user_id + '/courses?pt=full'
	courses_list_request = 	s.get(courses_url, verify=False)
		
	course_json = courses_list_request.json()
	selected_course_id = ''
	for course in course_json:
		if course[u'shortName'].strip() == courseid:
			selected_course_id = course[u'id'].strip()
			print 'found: ' +  course[u'shortName'] + ' - ' + course[u'longName'] + ' [' + course[u'id'] + ']'
	
	if selected_course_id == '':
		print 'Cannot find ' + selected_course_id
		sys.exit(1)	
	
	# GET course info
	courses_info_request = s.get(pod_host + '/WebObjects/LZTeacher.woa/ra/courses/' + selected_course_id + '?pt=full', verify=False)
	courses_info = courses_info_request.json()
	
	
	# UPLOAD files
	for subdir, dirs, files in os.walk(path):
		for fname in files:
		
			# DTS-specific (we only want MP4s that do not end with _lo)
			if fname.endswith('mp4') and not fname.endswith('_lo.mp4'):
				print fname
				
				# Check for previous upload
				already_uploaded = False
				for material in courses_info[u'materials']:
					if str(material[u'fileName']).strip() == fname:
						already_uploaded = True
						
				if already_uploaded:
					print ' - already uploaded'
					continue
				
				# GET UPLOAD URL
				courses_upload_url_request = s.post(pod_host + '/WebObjects/LZTeacher.woa/ra/courses/' + selected_course_id + '/uploads')
				upload_url = courses_upload_url_request.text.strip()
			
				# DO UPLOAD
				print '- uploading'
				file_path = path + '/' + fname
				files  = {'uploadMaterialInputName': (fname, open(file_path, 'rb'))}
				upload_file_request = requests.post(upload_url, files=files)
	
	# Done!
	print 'FINISHED'
	sys.exit(1)
	
if __name__ == "__main__":
    main(sys.argv[1:])