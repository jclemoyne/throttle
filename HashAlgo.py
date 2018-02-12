
import base64
import hashlib
import uuid
import random
import string
import math
from collections import OrderedDict

'''
	by Jean Claude Lemoyne 
	Feb 9, 2018
	For dollar shave club
'''

'''
	Write an Hash algorithm that will come up with unique string of 8 char length following the below rules
	Can use the below characters and digits
		i) 0 to 9 digits
		ii) A-Z characters
		iii) special characters
		iv) Collision probability is less than 1 in trillion

	Several methods are shown here
	note: 	UUID utilizes md5 (uuid.uuid3())hash function internally 
			uuid.uuid4() is random
			uuid.uuid5() is based on SHA-1
			uuid.uuid2() is based on host
			
	UUIDs have 122 bits of entropy so the chance of two random UUIDs colliding is about 10^-37
			
'''


def hashal(w, n=8):

	print '~~~~~~~ input: %s ~~~~~~~~~' % w
	hashcode1 = base64.encodestring(w)[:n]
	print 'hash code 1: %s ' % hashcode1

	hashmd5 = hashlib.md5(w)

	hashcode2 = hashmd5.hexdigest()[:n]
	print 'hash code 2: %s ' % hashcode2

	hashcode3 = hashmd5.digest().encode('base64')[:n]
	print 'hash code 3: %s ' % hashcode3

	hashsha = hashlib.sha256(w)
	hashcode4 = hashsha.digest().encode('base64')[:n]
	print 'hash code 4: %s ' % hashcode4

	hashcode5 = hashmd5.digest().encode('base64')[:n]
	print 'hash code 5: %s ' % hashcode5

	print '~~~~~ UUID ~~~~~'
	print ' uuid1: %s ' % uuid.uuid1()
	print ' uuid3: %s ' % uuid.uuid3(uuid.NAMESPACE_DNS, 'media.org')
	print ' uuid4: %s ' % uuid.uuid4()
	print ' uuid5: %s ' % uuid.uuid5(uuid.NAMESPACE_DNS, 'media.org')

	print '~~~~~ Randomly ~~~~~~'
	hrcode1 = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(n)])
	print ' random 1: %s ' % hrcode1

	print '~~~~~ Probability ~~~~~'
	k = 8
	N = 62 ** 8		# approx 52 letters and 10 digits not counting special characters
	punique = math.exp(-0.5 * k * (k - 1) / N)
	print 'probability of uniqueness: %e' % punique
	print 'probability of collision: %e' % (1 - punique)

'''
	Generate a hash without losing its order
'''


def orderedhash():
	ordict=OrderedDict()
	ordict['ac'] = 33
	ordict['gw'] = 20
	ordict['ap'] = 102
	ordict['za'] = 321
	ordict['bs'] = 10
	for k, v in ordict.items():
		print k, v


if __name__ == '__main__':
	orderedhash()
	hashal('jeanclaudelemoyne')
	hashal('JeanClaudeLemoyne')