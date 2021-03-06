# Import python modules
import numpy as np
import kaggle
from sklearn.metrics import accuracy_score
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import KFold
import pandas as pd
# Read in train and test data
def read_image_data():
	print('Reading image data ...')
	temp = np.load('../../Data/data_train.npz')
	train_x = temp['data_train']
	temp = np.load('../../Data/labels_train.npz')
	train_y = temp['labels_train']
	temp = np.load('../../Data/data_test.npz')
	test_x = temp['data_test']
	return (train_x, train_y, test_x)

############################################################################
train_x, train_y, test_x = read_image_data()
print('Train=', train_x.shape)
print('Test=', test_x.shape)

# Output file location
def kagglizing(predicted_y, best):
    file_name = '../Predictions/' + best + '.csv'
    # Writing output in Kaggle format
    print('Writing output to ', file_name)
    kaggle.kaggleize(predicted_y, file_name)

# Function to perform grid search fit the training data with kfold and predit the test labels
# with the best classifier selected returned from gridSearchcv function and return 
# errors for cv scores and 
def gridFunction(clf, parameter, folds):
    scoring = {'accuracy': make_scorer(accuracy_score)} # scoring = Accuracy
    grid = GridSearchCV(clf, param_grid= parameter, cv = folds, scoring= "accuracy") # performing gridsearch
    grid.fit(train_x, train_y) # fitting the data on gridsearch
    best_clf = grid.best_estimator_ #taking the best estimator 
    best_clf.fit(train_x, train_y) # fitting the training data in the best estimator
    predicted_y = best_clf.predict(test_x)  # predicting the test data
    print("The best parameter: ", grid.best_params_) 
    print("grid Score for the best parameter: ", grid.grid_scores_)
    return grid.best_params_, grid.grid_scores_, predicted_y
   
# Performing Decision Tree with tree depths = [3, 6, 9, 12, 14] and also using k fold cv for k  = 5
clf = DecisionTreeClassifier()
parameter = {"max_depth" : [3, 6, 9, 12, 14]}
best_param_dt, grid_scores_dt, predicted_y_dt = gridFunction(clf, parameter, 5)
kagglizing(predicted_y_dt, "best_dt")

# performing KneighestNeighbolours with neighnors [3; 5; 7; 9; 11]
clf = KNeighborsClassifier()
parameter = {"n_neighbors" : [3, 5, 7, 9, 11]}
best_param_kn, grid_scores_kn, predicted_y_kn = gridFunction(clf, parameter, 5)

acc = {"3":[], "5":[], "7":[], "9":[], "11":[]}
clf = KNeighborsClassifier(n_neighbors=11)
k_fold = KFold(n_splits= 5, shuffle = True)
for k, (train_index, test_index) in enumerate(k_fold.split(train_x, train_y)):      
    X_train, X_test = train_x[train_index], train_x[test_index]
    y_train, y_test = train_y[train_index], train_y[test_index]
    clf.fit(X_train, y_train)
    print("Fitting Done Now Predicting....")
    pred_y = clf.predict(X_test)
    print("Accuracy Score", accuracy_score(y_test, pred_y))
    acc["11"].append(accuracy_score(y_test, pred_y))

clf = KNeighborsClassifier(n_neighbors=3)
clf.fit(train_x, train_y)
pred_y = clf.predict(test_x)
kagglizing(pred_y, "bestKNN")

# Training linear model with alpha = [10**(-6), 10**(-4), 10**(-2), 1, 10]
parameter = {'loss' : ['hinge', "squared_loss"], 'alpha' : [10**(-6), 10**(-4), 10**(-2), 1, 10]}
clf = SGDClassifier()
best_param_lm, grid_scores_lm, predicted_y_lm = gridFunction(clf, parameter, 5)
kagglizing(predicted_y_lm, 'best_lm')





 

"""
# Create dummy test output values to compute accuracy
test_y = np.ones(test_x.shape[0])
predicted_y = np.random.randint(0, 4, test_x.shape[0])
print('DUMMY Accuracy=%0.4f' % accuracy_score(test_y, predicted_y, normalize=True))
"""



