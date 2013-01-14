#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
iTunes U Course Manager - Create Posts from Materials and Outline

Author: John Dyer <http://j.hn/> @johndyer
Company: Dallas Theological Seminary <http://www.dts.edu/> @dallasseminary
Dependencies: Python 2.7, requests

USAGE:
$ python itunesu.py -u USERNAME -p PASSWORD -c COURSESHORTNAME

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
	
	# PARSE Command Line
	opts, args = getopt.getopt(argv, 'u:p:c:i:')
	
	for opt, arg in opts:                
		if opt in ("-u"):      
			username = arg
		elif opt in ("-p"):
			password = arg
		elif opt in ("-c"):
			courseid = arg
			
	if username == '' or password == '':
		print 'Missing username (-u) or password (-p)'
		sys.exit(1)
	if courseid == '':
		print 'Missing course shortname (-c)'
		sys.exit(1)
	
	# LOGIN
	s = requests.session()
	headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2", "Content-Type": "application/json"}
	
	print "Logging in with " + username
	payload = {'enteredUsername':username,'password':password}
	login_request = s.post("https://itunesu.itunes.apple.com/WebObjects/LZDirectory.woa/ra/login", data=payload, verify=False)
	login_data = login_request.text.strip()

	if login_data == 'unauthorized':
		print '-Error logging in'
		sys.exit(1)

	logged_in_user_id = login_request.json()[u'personId']
	print " - logged in as: " + str(logged_in_user_id)
	
	
	# WAKE to get correct URL
	wake_data = s.get('https://itunesu.itunes.apple.com/WebObjects/LZDirectory.woa/ra/wake/')
	pod_host = str(wake_data.json()[u'podHost'])
	
	
	# FIND course
	print "Getting list of courses"
	courses_url = pod_host + '/WebObjects/LZTeacher.woa/ra/teachers/' + str(logged_in_user_id) + '/courses?pt=full'
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
	course_info_request = s.get(pod_host + '/WebObjects/LZTeacher.woa/ra/courses/' + selected_course_id + '?pt=full', verify=False)
	course_info = course_info_request.json()
	
	
	# Get topics
	ordered_topics = get_ordered_main_topics(course_info[u'topics'])	
	
	
	# Go through Topics and create posts for matching videos 
	new_index = 0
	for tindex, topic in enumerate(ordered_topics):
		
		print str(tindex+1) + '. ' + topic[u'name'] + ' : ' + topic[u'externalId']
		
		# Check for existing posts in this topic with 'Video' in the title
		found_video_post = False
		for post in course_info[u'posts']:
			if str(post[u'topic']) == str(topic[u'externalId']) and str(post[u'title']).find('Watch') > -1:
				found_video_post = True
				continue
		
		if found_video_post:
			print ' - skipping (already has video post)'
			continue
		
		# find all materials that have this unit number in it (BE101_u010_v002.mp4 looking for the '10' or 'u010')
		materials_in_unit = []
		for material in course_info[u'materials']:
			if str(material[u'fileName']).find('u' + str(tindex+1).zfill(3) ) > -1:
				materials_in_unit.append(material)
				print ' - ' + material[u'fileName']

		# create numbers for the 'new-5' format
		new_index = new_index+1
		new_post_number = new_index
			
		# if we have materials, then create a post
		if len(materials_in_unit) > 0:
		
			# create activities (i.e. files) list
			activities = []
			for mindex, material in enumerate(materials_in_unit):
				new_index = new_index+1
				try:
					simple_name = str(material[u'name'])
					simple_name = simple_name[simple_name.find(' - ')+3:]
					material_list = []
					material_list.append(str(material[u'externalId']))
					activity = {"externalId":"new-" + str(new_index),"message":simple_name,"startMarker":"0","endMarker": str(material[u"duration"]),"rank":(mindex+1),"materials":material_list,"dueDate":None}
					activities.append(activity)	
				except:
					print 'ERROR ' + material[u'name']
		
			print '- creating Post'
			print '' 
					
			# Create topic post JSON data
			payload = {"title":"Watch Videos","message": "<div>Watch these " + str(len(materials_in_unit)) + " videos.</div>", "authorAppleId": logged_in_user_id, "topic": str(topic[u"externalId"]), "rankForTopic": topic[u"rank"], "externalId": "new-" + str(new_post_number), "course": str(selected_course_id), "postState": "PUBLISHED", "activities": activities}
			
			"""
			print '---- create post JSON data ----'
			print payload			
			print '' 
			"""
	
			# Send to iTunes U
			create_post = s.post(pod_host + '/WebObjects/LZTeacher.woa/ra/courses/' + selected_course_id + '/posts?c=complex', data=json.dumps(payload), verify=False, headers=headers)
			create_post_json = create_post.json()
			
			"""
			print '---- result ----'
			print create_post_json
			print ''
			"""
			
		else:
			print ' - No materials with ' + str(tindex+1).zfill(3)  + ' in it.'
	
	
	print 'FINISHED'
	sys.exit(1)
	
	
# Function to find and re-order top level topics
def get_ordered_main_topics(topics):
	top_level_topics = []
	for topic in topics:
		if topic[u'indentationLevel'] == 0:
			top_level_topics.append(topic)
	
	# Sort by the 'rank'
	ordered_topics = sorted(top_level_topics, key=lambda topic: topic[u'rank'])

	return ordered_topics
	
if __name__ == "__main__":
    main(sys.argv[1:])