import numpy as np
from sklearn.model_selection import train_test_split


def load_train_data(mal_file, ben_file):

    mal_data = np.loadtxt(mal_file)
    ben_data = np.loadtxt(ben_file)


    data = np.vstack((mal_data, ben_data))


    X = data[:, :-1]  
    y = data[:, -1]  

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test

# 新增：加载测试数据
def load_test_data(mal_file, ben_file):

    mal_data = np.loadtxt(mal_file)
    ben_data = np.loadtxt(ben_file)


    data = np.vstack((mal_data, ben_data))


    X_test = data[:, :-1]  
    y_test = data[:, -1]  


    return X_test, y_test