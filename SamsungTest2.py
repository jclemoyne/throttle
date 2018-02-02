import os
import numpy as np
from scipy import ndimage
import cv2 # OpenCV

# By Jean Claude Lemoyne - January 30, 2018
# This code was prepared for Samsung
# phone: 415-845-9238
# Code is in Python 2.7
# Anaconda Environment


'''
	Write a function to rotate an array to the right by a specified factor.
	example: Input array [ 1,2,3,4,5,6,7 ]
	Rotate to right by 4 Output array[ 4, 5,6,7,1,2,3]
'''


def problem1(a, n):
	# mathematically this is a circular permutation
	# use numpy roll
	print a
	print np.roll(a, n)


'''
	Write a function to take one integer input buffer, 
	and another list of integer values. 
	Return how many times each of the integer values are in the buffer
'''


def problem2(i, b):
	print b
	print list(b).count(i)


'''
	Given a MxN integer matrix whose element is either 0 or 1 randomly. Now we define
	"Connected Regions" as one defined by 1s' -
	Assign a region number to each element 	  
'''


def problem3(m1):
	print '== connected graph matrix ==='
	print m1
	labels, nb = ndimage.label(m1)
	print '== labeled region matrix == ', labels
	print '# of labeled connected region: ', nb


'''
	REMARK:
	=======
	How to handle this problem:
	Suppose you are running this program on an embedded device with only 256MB 
	memory, and the matrix is super large like several GB’s saved on a file in the disk. 
	How would you update the matrix in that file the same with question 1? 
	(Please explain here how to handle. (Not coding)
	
	1) 	The 5GB image has to reside somewhere we assume it is residing in a data storage of some sort
	2) 	The bst model to use is of Virtual Memory i.e. extending RAM into Disk Storage
	3) 	This Virtual Memory setup should be transparent to the application
	4) 	The application would deal with the virtual size and the Virtual Memoty System (VMS) will
		take care of swapping virtual pages (chunks of arrays) into memory for processing 
	
'''


'''
	OpenCV part
'''


'''
	Using OpenCV (opencv-python) import cv2
	img here is .jpg
	Note: np.reshape is time consuming; there are alternative methods without
	reshaping
'''


def problem4(imgfile):
	# read image
	imgpath = os.path.abspath(os.path.curdir) + '/' + imgfile
	print '... image file: ', imgpath
	if not os.path.exists(imgpath):
		print ' *** FILE ', imgpath, ' NOT FOUND!!'
		return

	color_image = cv2.imread(imgpath)
	print '... image ', img, ' read!'
	# convert to gray scale
	gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
	gray_imgfile = 'gray_' + imgfile
	cv2.imwrite(gray_imgfile, gray_image)
	print ' ... gray image file ', gray_imgfile, ' saved!'
	# calculate mean
	average_color = gray_image.mean()
	n, m = gray_image.shape
	print ' ~~ image shape: ', gray_image.shape
	linear_img = np.reshape(gray_image, -1)
	print linear_img.shape
	print ' ~~ average gray color: ', average_color
	mapped_linear_image = map(lambda px: 0 if px < average_color else px, linear_img)
	mapped_image = np.reshape(mapped_linear_image, (n, m))
	map_avg_gray_imgfile = 'mat_avg_gray_' + imgfile
	cv2.imwrite(map_avg_gray_imgfile, mapped_image)
	print ' ... mapped avg gray image file ', map_avg_gray_imgfile, ' saved!'


if __name__ == '__main__':
	np.random.seed(424526)
	a = np.arange(1, 8)
	problem1(a, 4)

	b = np.random.randint(1, 5, 20)
	problem2(2, b)

	# m1 = np.random.randint(0, 2, (4, 5))
	m1 = np.array([[1, 1, 0, 0, 1], [1, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 1, 1, 0, 0]])
	problem3(m1)

	# using this example - may use any example in current directory
	img = 'Aerial08.jpg'
	problem4(img)

