# Import modules
import numpy as np
import pickle
import random
import pprint
from scipy import misc
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error


def read_scene():
	data_x = misc.imread('../../Data/Scene/times_square.jpg')
	return (data_x)

def read_faces():
	nFaces = 100
	nDims = 2500
	data_x = np.empty((0, nDims), dtype=float)

	for i in np.arange(nFaces):
		data_x = np.vstack((data_x, np.reshape(misc.imread('../../Data/Faces/face_%s.png' % (i)), (1, nDims))))

	return (data_x)

def k_mean_clustering(k, flattened_image):
	# Function to perform k_mean_clustering and calculating the 
	# SSE for each pixel with its centroid 
	# input is image and k 
	# returns flatter reconstructed image, reconstructed image
	# and array of sse of pixels to its centroid.
	clf = KMeans(n_clusters=k)
	clf.fit(flattened_image)
	labels = clf.predict(flattened_image)
	print("Fitting and predicting done for k " + str(k))
	re_image = np.zeros((flattened_image.shape))
	squared_error = 0
	for pixel in range(flattened_image.shape[0]):
		cluster_center = clf.cluster_centers_[labels[pixel]]
		squared_error += mean_squared_error(flattened_image[pixel], cluster_center)
		re_image[pixel] = cluster_center
	re_image = re_image/255
	return re_image, re_image.reshape(400, 400, 3), np.log(squared_error)

def rmse(predictions, targets):
	# Function calculates the Root mean squared error
    return np.sqrt(((predictions - targets) ** 2).mean())

def cov(data_x):
	# helper function to calculate the covariance matrix
	# getting the eigen value and vector and sorted them as per eigen value
	# Input is dataset, returns eig vector ranked from highest to lowest eig value
	cov = np.cov(data_x.T)
	v, w =  np.linalg.eigh(cov)
	
	eig_rank = []
	for i in range(len(v)):
		eig_rank.append(((np.abs(v[i]), w[:,i])))
	eig_rank.sort(key=lambda x: x[0], reverse=True)
	return eig_rank

def PCA(eig_rank, K):
	# Helper function to return the reconstructed image takes the eig_rank and k 
	# returns Reconstructed X, lower dimension projected X and Wk
	W = []
	for k in range(K):
		W.append(eig_rank[k][1])
	W = np.array(W)
	X_projected = data_x.dot(W.T)
	X_recon = X_projected.dot(W)
	return X_recon, X_projected, W

if __name__ == '__main__':
	
	################################################
	# PCA

	# Reading data 
	data_x = read_faces()
	print('X = ', data_x.shape)
	print('Implement PCA here ...')

	# Getting the Eigen value and eigen vector from the Con function
	eig_rank = cov(data_x)

	#getting the k best eigenvalues
	# for each of k and ploting the face1.png 
	# and its 8 reconstructed images in
	# plot.
	K = [3,5,10,30,50,100,150,300]

	# Variable to store the Reconstruction error
	# and compression rate and print them
	recons_error = [["K", "Reconstruction Error", "Compression Rate"]] 

	# Ploting 3*3 grid plot with one original and 
	# and 8 reconstructed image of face1.png file
	f, ax = plt.subplots(3, 3)
	ax = ax.ravel()
	ax[0].imshow(data_x[1].reshape(50, 50))
	ax[0].set_title("Original Photo", fontsize=6)
	for i, k in enumerate( K):
		X_recon, X_projected, W = PCA(eig_rank, k)
		err = rmse(X_recon, data_x)
		recons_error.append([k,err, (X_projected.nbytes + W.nbytes) / data_x.nbytes])
		ax[i + 1].imshow(X_recon[1].reshape(50, 50))
		ax[i + 1].set_title("Reconstructed Image for K: " + str(k), fontsize=6)
	f.tight_layout()
	f.savefig("../Figures/PCA.png")
	plt.close()
	# Printing the recons_error Variable
	print("*"*10 + "Average Squared Reconstruction Error and Compression Rate" + "*"*10)
	pprint.pprint(recons_error)


	################################################
	# K-Means

	# Reading data
	data_x = read_scene()
	print('X = ', data_x.shape)

	# Reshaping the data 
	flattened_image = data_x.ravel().reshape(data_x.shape[0] * data_x.shape[1], data_x.shape[2])
	print('Flattened image = ', flattened_image.shape)
	print('Implement k-means here ...')
	
	# Different K's to work as asked in the questions.
	K = [2, 5,10,25,50,75,100,200] 
	result = [] # Result takes the reconstructed image and pickle to save.p
	SSE = [] # Sum of Squared error
	# Ploting the 3*3 plot with one original and 
	# 8 reconstructed images.
	f, ax = plt.subplots(3, 3)
	ax[0, 0].imshow(data_x)
	ax[0, 0].set_title("Original Image", fontsize=6)
	for i, k in enumerate(K):
		i = i + 1
		re_image, new_image, squared_error = k_mean_clustering(k, flattened_image)
		result.append(re_image); SSE.append(squared_error)
		#print(int((i - i%3)/3), int(i - int(i/3)*3))
		ax[int((i - i%3)/3), int(i - int(i/3)*3)].imshow(new_image)
		ax[int((i - i%3)/3), int(i - int(i/3)*3)].set_title("Reconstructed image for k - " + str(k), fontsize = 6)
	plt.tight_layout()
	#Helper Code to save the result of the K-means so that we dont have to run the model
	# again and again.
	plt.savefig("../Figures/Reconstructed_image.png")
	plt.close()
	pickle.dump(result, open( "save.p", "wb" ) )
	recons_image = pickle.load( open( "save.p", "rb" ) )
	recons_error = []
	for i, k in enumerate(K):
		err = rmse(recons_image[i], flattened_image/255)
		recons_error.append((k,err))

	#Working on the reconstruction Error
	print("*"*10 + "Reconstruction Error" + "*"*10)
	pprint.pprint(recons_error)

	# Working on the Compression Ration
	print("*"*10 + "Compression Ratio"+ "*"*10)
	for k in K:
		pixels = data_x.shape[0] * data_x.shape[1]
		tmp = (32*3*k + pixels*np.log2(k))/(24*pixels)  
		print("For K equals: " + str(k) + " compression ratio is: "  + str(tmp))
	# Working on the Elbow Graph
	print("*"*10 + "Elbow Graph" + "*"*10)
	plt.scatter(K, SSE, c='r')
	plt.plot(K, SSE)
	plt.ylabel("Sum of Squared error (log)")
	plt.xlabel("Number of cluster (k)")
	plt.title("Sum of Squared Error of Each Pixel from Centroids")
	plt.savefig("../Figures/kmeanElbow.png")