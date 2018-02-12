import csv

'''
	by Jean Claude Lemoyne for dollar shave club
	This problem makes sense only for online sessions (usually 30 minutes)
	online user activities on a given website are sessionized 
	i.e. a UUID is provided if there is no registration or user account
	i.e. the same user may have several UUIDs'
'''


def make_link_list(path):
	browse = dict()
	with open(path, 'rb') as csvfile:
		xreader = csv.reader(csvfile, delimiter=',', quotechar='"')
		nn = 0
		for row in xreader:
			#print row
			nn = nn + 1
			if nn == 1:
				hdr = row
				for col in hdr:
					print col
					print "___________________"
			else:
				hashrow = dict(zip(hdr, row))
				event_id = hashrow['event_id']
				userid = hashrow['domain_userid']
				tstamp = hashrow['collector_tstamp']
				page_url = hashrow['page_urlpath']
				if userid not in browse:
					browse[userid] = [(tstamp, event_id, page_url)]
				else:
					browse[userid] = browse[userid] + [(tstamp, event_id, page_url)]
				# print hashrow
	hdr = hdr + ['next_event_id']
	cols = ','.join(hdr)
	g = open('linked_' + path, 'w')
	g.write(cols + '\n')
	for idx, userid in enumerate(browse):
		browse[userid] = sorted(browse[userid], key=lambda tup: tup[0])
		linklen = len(browse[userid])
		for i, tup in enumerate(browse[userid]):
			next_event_id = '~'
			if i + 1 < linklen:
				next_event_id = browse[userid][i + 1][1]
			row = '%s,%s,%s,%s,%s\n' % (tup[1], tup[0], userid, tup[2], next_event_id)
			g.write(row)
		print '[%d] ' % idx, ' ', userid, browse[userid	]

	print '.. total read: %d' % nn
	avg = nn / len(browse)
	print '.. avg # pages per user: %d' % avg
	print cols
	g.close()


if __name__ == '__main__':
	make_link_list('data1.csv')