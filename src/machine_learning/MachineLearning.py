from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler, RobustScaler
from sklearn.metrics import recall_score, precision_score, roc_auc_score, mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score, confusion_matrix, classification_report, accuracy_score
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import tensorflow as tf
from sklearn.model_selection import train_test_split

from prettytable import PrettyTable

import pickle
import sys
import os
import pandas as pd
import numpy as np
import urllib.request
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import optuna
import xgboost
import re
from nltk.text import stopwords

def Mejor_PCA_DecissionTree_Regression(X_train, X_test, y_train, y_test, metric, 
                                        list_maxComponents, list_maxDepth, list_maxFeatures):
    '''
    Funcion a la que se le pasa los datos de train, test, tipo de metrica, asi como los parametros del PCA y
    DecisionTreeRegressor, y devuelve los valores optimos de predicion, metrica y mejores parametros.
    
    Los parametros pasados son en el caso del:
        PCA: se pasa una lista con el n_components
        DecisionTreeRegressor: se pasa una lista con el max_depth, y otra lista con el max_features
    Argumentos:
        X_train (DataFrame): Cointains the independents vars splitted for training
        X_test (DataFrame):  Cointains the independents vars splitted for test
        y_train (DataFrame): Cointains the dependents vars splitted for training
        y_test (DataFrame): Cointains the dependents vars splitted for test
        metric (str): nombre de la metrica a utilizar en la prediccion. 
            Valores posibles ['mae','mape','mse','r2_score']
        list_maxComponents (list): lista con el n_components del PCA
        list_max_depth (list): lista con el max_depth del DecisionTreeRegressor
        list_maxFeatures (list): lista con el max_features del DecisionTreeRegressor
        Ejemplos:
            list_maxComponents = [ 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
            list_maxDepth = [ 2, 3, 5, 10, 20, 30, 40]
            list_maxFeatures = [ (1/17), (2/17), (3/17), (4/17), (5/17), (6/17), (7/17), (8/17), (9/17), (10/17), (11/17), (12/17), (13/17), (14/17), (15/17), (16/17), (17/17)]
    Retornos:
        y_pred (array): los valores optimos de la predicción
        metric_Best (float): el optimo valor de la metrica para los parametros dados
        n_components (int) el parametro optimo n_components del PCA
        max_depth (int): lista con el max_depth del DecisionTreeRegressor
        maxFeatures (float): lista con el maxFeatures del DecisionTreeRegressor
    '''
    # Escala los datos de train y test
    ss = StandardScaler()
    X_train_scaled = ss.fit_transform(X_train)
    X_test_scaled = ss.transform(X_test)
    
    n = 0 # Para indicar si es la primera vez
    for componentsi in list_maxComponents:
        pca = PCA(n_components=componentsi, random_state=42)
        pca.fit(X_train_scaled)
        X_train_scaled_pca = pca.transform(X_train_scaled)
        X_test_scaled_pca = pca.transform(X_test_scaled)
        for depthi in list_maxDepth:
            for featuresi in list_maxFeatures:
                dtr = DecisionTreeRegressor(max_depth = depthi, max_features = featuresi, random_state=42)
                dtr.fit(X_train_scaled_pca, y_train)
                y_pred = dtr.predict(X_test_scaled_pca)
                if (n == 0): # La primera vez se inicializa
                    if(metric == 'mae'):
                        metric_Best = mean_absolute_error(y_test, y_pred)
                    elif(metric == 'mape'):
                        metric_Best = mean_absolute_percentage_error(y_test, y_pred)
                    elif(metric == 'mse'):
                        metric_Best = mean_squared_error(y_test, y_pred)
                    elif(metric == 'r2_score'):
                        metric_Best = r2_score(y_test, y_pred)
                    else:
                        sys.exit('metric debe ser una de [\'mae\',\'mape\',\'mse\',\'r2_score\']')
                    max_components_Best = componentsi
                    max_depth_Best = depthi
                    max_features_Best = featuresi
                else:
                    if(metric == 'mae'):
                        metric_New = mean_absolute_error(y_test, y_pred)
                    elif(metric == 'mape'):
                        metric_New = mean_absolute_percentage_error(y_test, y_pred)
                    elif(metric == 'mse'):
                        metric_New = mean_squared_error(y_test, y_pred)
                    elif(metric == 'r2_score'):
                        metric_New = r2_score(y_test, y_pred)
                    else:
                        sys.exit('metric debe ser una de [\'mae\',\'mape\',\'mse\',\'r2_score\']')

                    if (metric == 'mae') or (metric == 'mape') or (metric == 'mse'): # Minimize
                        if (metric_New < metric_Best):
                            metric_Best = metric_New
                            max_components_Best = componentsi
                            max_depth_Best = depthi
                            max_features_Best = featuresi
                    if (metric == 'r2_score'): # Maximize
                        if (metric_Best < metric_New):
                            metric_Best = metric_New
                            max_components_Best = componentsi
                            max_depth_Best = depthi
                            max_features_Best = featuresi
            n +=1
    return y_pred, metric_Best, max_components_Best, max_depth_Best, max_features_Best

def Mejor_PCA_RandomForest_Regression(X_train, X_test, y_train, y_test, metric, 
                                    list_maxComponents, list_n_estimators, list_max_leaf_nodes):
    '''
    Funcion a la que se le pasa los datos de train, test, tipo de metrica, asi como los parametros del PCA y
    RandomForestRegressor, y devuelve los valores optimos de predicion, metrica y mejores parametros
    
    Los parametros pasados son en el caso del:
        PCA: se pasa una lista con el n_components
        RandomForestRegressor: se pasa una lista con el n_estimators, y una lista con el max_leaf_nodes 
    Argumentos:
        X_train (DataFrame): Cointains the independents vars splitted for training
        X_test (DataFrame):  Cointains the independents vars splitted for test
        y_train (DataFrame): Cointains the dependents vars splitted for training
        y_test (DataFrame): Cointains the dependents vars splitted for test
        metric (str): nombre de la metrica a utilizar en la prediccion. 
            Valores posibles ['mae','mape','mse','r2_score']
        list_maxComponents (list): lista con el n_components del PCA
        list_n_estimators (list): lista con el n_estimators del RandomForestRegressor
        list_max_leaf_nodes (list): lista con el max_leaf_nodes del RandomForestRegressor
        Ejemplos:
            list_maxComponents = [ 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
            list_n_estimators = [10, 25, 50, 100, 200, 300, 500, 800, 1000]
            list_max_leaf_nodes = [5, 10, 15, 20, 25]
   
    Retornos:
        y_pred (array): los valores optimos de la predicción
        metric_Best (float): el optimo valor de la metrica para los parametros dados
        n_components (int): el parametro optimo n_components del PCA
        n_estimators (int): el parametro optimo n_estimators del RandomForestRegressor
        max_leaf_nodes (int): el parametro optimo max_leaf_nodes del RandomForestRegressor
    '''
    # Escala los datos de train y test
    ss = StandardScaler()
    X_train_scaled = ss.fit_transform(X_train)
    X_test_scaled = ss.transform(X_test)

    n = 0 # Para indicar si es la primera vez
    for componentsi in list_maxComponents:
        pca = PCA(n_components=componentsi, random_state=42)
        pca.fit(X_train_scaled)
        X_train_scaled_pca = pca.transform(X_train_scaled)
        X_test_scaled_pca = pca.transform(X_test_scaled)
        for n_estimatorsi in list_n_estimators:
            for max_leaf_nodesi in list_max_leaf_nodes:
                rnd_reg = RandomForestRegressor(n_estimators=n_estimatorsi, max_leaf_nodes=max_leaf_nodesi, random_state=42)
                rnd_reg.fit(X_train_scaled_pca, y_train)
                y_pred = rnd_reg.predict(X_test_scaled_pca)
                if (n == 0): # La primera vez se inicializa
                    if(metric == 'mae'):
                        metric_Best = mean_absolute_error(y_test, y_pred)
                    elif(metric == 'mape'):
                        metric_Best = mean_absolute_percentage_error(y_test, y_pred)
                    elif(metric == 'mse'):
                        metric_Best = mean_squared_error(y_test, y_pred)
                    elif(metric == 'r2_score'):
                        metric_Best = r2_score(y_test, y_pred)
                    else:
                        sys.exit('metric debe ser una de [\'mae\',\'mape\',\'mse\',\'r2_score\']')
                    n_estimators_Best = n_estimatorsi
                    max_leaf_nodes_Best = max_leaf_nodesi
                    max_components_Best = componentsi
                else:
                    if(metric == 'mae'):
                        metric_New = mean_absolute_error(y_test, y_pred)
                    elif(metric == 'mape'):
                        metric_New = mean_absolute_percentage_error(y_test, y_pred)
                    elif(metric == 'mse'):
                        metric_New = mean_squared_error(y_test, y_pred)
                    elif(metric == 'r2_score'):
                        metric_New = r2_score(y_test, y_pred)
                    else:
                        sys.exit('metric debe ser una de [\'mae\',\'mape\',\'mse\',\'r2_score\']')

                    if (metric == 'mae') or (metric == 'mape') or (metric == 'mse'): # Minimize
                        if (metric_New < metric_Best):
                            metric_Best = metric_New
                            n_estimators_Best = n_estimatorsi
                            max_leaf_nodes_Best = max_leaf_nodesi
                            max_components_Best = componentsi
                    if (metric == 'r2_score'): # Maximize
                        if (metric_Best < metric_New):
                            metric_Best = metric_New
                            n_estimators_Best = n_estimatorsi
                            max_leaf_nodes_Best = max_leaf_nodesi
                            max_components_Best = componentsi
            n +=1
    return y_pred, metric_Best, max_components_Best, n_estimators_Best, max_leaf_nodes_Best

def Mejor_PCA_XGB_Regression(X_train, X_test, y_train, y_test, metric, 
                            list_maxComponents, list_n_estimators, list_max_depth, list_learning_rate):
    '''
    Funcion a la que se le pasa los datos de train, test, tipo de metrica, asi como los parametros del PCA y
    XGBRegressor, y devuelve los valores optimos de predicion, metrica y mejores parametros.
    
    Los parametros pasados son en el caso del:
        PCA: se pasa una lista con el n_components
        XGBRegressor: se pasa una lista con el n_estimators, una lista con el max_depth, y 
            otra lista con el learning_rate
    Argumentos:
        X_train (DataFrame): Cointains the independents vars splitted for training
        X_test (DataFrame):  Cointains the independents vars splitted for test
        y_train (DataFrame): Cointains the dependents vars splitted for training
        y_test (DataFrame): Cointains the dependents vars splitted for test
        metric (str): nombre de la metrica a utilizar en la prediccion. 
            Valores posibles ['mae','mape','mse','r2_score']
        list_maxComponents (list): lista con el n_components del PCA
        list_n_estimators (list): lista con el n_estimators del XGBRegressor
        list_max_depth (list): lista con el max_depth del XGBRegressor
        list_learning_rate (list): lista con el learning_rate del XGBRegressor
        Ejemplos:
            list_maxComponents = [ 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
            list_n_estimators = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            list_max_depth = [5, 10, 15, 20, 25]
            list_learning_rate = [0.01, 0.1, 0.5, 0.75, 1, 1.25, 1.5]
    Retornos:
        y_pred (array): los valores optimos de la predicción
        metric_Best (float): el optimo valor de la metrica para los parametros dados
        n_components (int) el parametro optimo n_components del PCA
        n_estimators (int): el parametro optimo n_estimators del XGBRegressor
        max_depth (int): lista con el max_depth del XGBRegressor
        learning_rate (float): lista con el learning_rate del XGBRegressor
    '''
    # Escala los datos de train y test
    ss = StandardScaler()
    X_train_scaled = ss.fit_transform(X_train)
    X_test_scaled = ss.transform(X_test)

    n = 0 # Para indicar si es la primera vez
    for componentsi in list_maxComponents:
        pca = PCA(n_components=componentsi, random_state=42)
        pca.fit(X_train_scaled)
        X_train_scaled_pca = pca.transform(X_train_scaled)
        X_test_scaled_pca = pca.transform(X_test_scaled)
        for n_estimatorsi in list_n_estimators:
            for max_depthi in list_max_depth:
                for learning_ratei in list_learning_rate:
                    xgb_reg = XGBRegressor(n_estimators=n_estimatorsi, max_depth=max_depthi, learning_rate=learning_ratei, random_state=42)
                    xgb_reg.fit(X_train_scaled_pca, y_train)
                    y_pred = xgb_reg.predict(X_test_scaled_pca)
                    if (n == 0): # La primera vez se inicializa
                        if(metric == 'mae'):
                            metric_Best = mean_absolute_error(y_test, y_pred)
                        elif(metric == 'mape'):
                            metric_Best = mean_absolute_percentage_error(y_test, y_pred)
                        elif(metric == 'mse'):
                            metric_Best = mean_squared_error(y_test, y_pred)
                        elif(metric == 'r2_score'):
                            metric_Best = r2_score(y_test, y_pred)
                        else:
                            sys.exit('metric debe ser una de [\'mae\',\'mape\',\'mse\',\'r2_score\']')
                        n_estimators_Best = n_estimatorsi
                        max_depth_Best = max_depthi
                        learning_rate_Best = learning_ratei
                        max_components_Best = componentsi
                    else:
                        if(metric == 'mae'):
                            metric_New = mean_absolute_error(y_test, y_pred)
                        elif(metric == 'mape'):
                            metric_New = mean_absolute_percentage_error(y_test, y_pred)
                        elif(metric == 'mse'):
                            metric_New = mean_squared_error(y_test, y_pred)
                        elif(metric == 'r2_score'):
                            metric_New = r2_score(y_test, y_pred)
                        else:
                            sys.exit('metric debe ser una de [\'mae\',\'mape\',\'mse\',\'r2_score\']')

                        if (metric == 'mae') or (metric == 'mape') or (metric == 'mse'): # Minimize
                            if (metric_New < metric_Best):
                                metric_Best = metric_New
                                n_estimators_Best = n_estimatorsi
                                max_depth_Best = max_depthi
                                learning_rate_Best = learning_ratei
                                max_components_Best = componentsi
                        if (metric == 'r2_score'): # Maximize
                            if (metric_Best < metric_New):
                                metric_Best = metric_New
                                n_estimators_Best = n_estimatorsi
                                max_depth_Best = max_depthi
                                learning_rate_Best = learning_ratei
                                max_components_Best = componentsi
            n +=1
    return y_pred, metric_Best, max_components_Best, n_estimators_Best, max_depth_Best, learning_rate_Best

def scaler(scaler: str, data: np.array):
    '''
    Scales the data.
    Args:
        scaler: A scaler to choose from sklearn library. StandardScaler, MinMaxScaler, MaxAbsScaler, RobustScaler
        data: Matrix like data to be scaled. Has to be a minimum of two dimensions.
    
    Returns:
        The data scaled.
    '''
    try:
        if scaler=='StandardScaler':
            return StandardScaler().fit_transform(data)
        if scaler=='MinMaxScaler':
            return MinMaxScaler().fit_transform(data)
        if scaler=='MaxAbsScaler':
            return MaxAbsScaler().fit_transform(data)
        if scaler=='RobustScaler':
            return RobustScaler().fit_transform(data)
            
    except ValueError:
        print('Choose one of the scalers listed or pass through a matrix of at least two dimension for data.')
        
    
def prediction(model, X_test, y_pred=None):
    ''' 
    Realizar predicciones del modelo de machine learning sobre la parte de test.
    Args:
        model: modelo entrenado.
        X_test: variable que contiene las 'features' de la parte de test.
        y_test: variable que contiene la 'target' de la parte de test.
    Return:
       preds: Un array con las predicciones realizadas.
    '''
    try:
        if type(y_pred)!=type(None):
            print('Score:',model.score(X_test,y_pred))
        preds = model.predict(X_test).round(0)
        return preds
    except:
        print('Error en la predicción')

def class_results(y_test, pred_y):
    ''' 
    Resultados obtenidos a partir de un modelo de classificación.
    Args:
        y_test: variable con la 'target' de test.
        pred_y: variable con las predicciones sobre el test.
    Return:
        Reporte sobre los resultados obtenidos.
        Matriz de confusión mostrada con un 'heatmap' de seaborn.
    '''
    conf_matrix = confusion_matrix(y_test, pred_y)
    plt.figure(figsize=(9,6))
    sns.heatmap(conf_matrix, annot=True,fmt="")
    plt.title('Confusion matrix')
    plt.ylabel('True class')
    plt.xlabel('Predicted class')
    return (classification_report(y_test, pred_y))

def binary_class_metrics(y_train, y_test):
    ''' 
    Resultado de las métricas de accuracy, precision, recall y
    f1 score para modelos de clasificación binaria.
    Args:
        y_train: variable con la 'target' de la parte de train.
        y_test: variable con la 'target' de la parte de test.
    
    Return:
        Print de las 4 métricas indicadas: accuracy, precision,
        recall, f1 score.
    '''
    from sklearn import metrics

    accuracy = metrics.accuracy_score(y_train, y_test)
    print('Accuracy score:', accuracy)

    precision = metrics.precision_score(y_train, y_test)
    print('Precision score:', precision)

    recall = metrics.recall_score(y_train, y_test)
    print('Recall score:', recall)

    f1_score = metrics.f1_score(y_train, y_test)
    print('F1 score:', f1_score)
    
    return accuracy, precision, recall, f1_score

def precision_recall_AUC(y_test, y_pred):
    ''' 
    Resultado de la métrica AUC a partir del modelo entrenado.
    Args:
        y_test: variable con la 'target' de la parte de test.
        y_pred: variable con la las predicciones sobre la 'target'.
    
    Return:
        El score de AUC en base a los argumentos indicados.
    '''
    recall = recall_score(y_test, y_pred).round(3)
    precision = precision_score(y_test, y_pred).round(3)
    auc = roc_auc_score(y_test, y_pred).round(3)

    return print('Precision:', precision,',', 'Recall:', recall,',', 'ROC AUC score:', auc)

def load_model(model_path):
    '''
    Carga el modelo
       loads model 
        
    Argumentos: 
       directorio de modelo = pesos del modelo 
       arguments: 
       model path = model weights 
    '''
    
    model = tf.keras.models.load_model(model_path)

    return model

def XgBoost_X_y(X,y,size,random):
    '''
    Función para seleccionar nuestras variables X e y, tamaño del test y random state.
    Args: 
        X : Variable X
        y : Variable target
        size : tamaño del test
        random : numero de random state.
    
    Return:
        Función objectiveXgboost
    '''
    X_train_ex, X_test_ex, y_train, y_test =  train_test_split(X, y, test_size = size, random_state = random)

    def objectiveXgboost(trial):
        """
        Función que llama a la anterior ''XgBoost_X_y'' y elige diferentes parametros por optimización bayesania.
        Args: 
            trial : Las veces que se recorrera los parametros para que Optuna eliga el mejor, se le añadira un numero entero.
        Return:
            Accuracy.
        """
        scaler=StandardScaler()
        X_train=scaler.fit_transform(X_train_ex)
        X_test=scaler.fit_transform(X_test_ex) 
        dtrain = xgboost.DMatrix(X_train, label=y_train) 
        dtest = xgboost.DMatrix(X_test, label=y_test)

        
        param = {
            "silent": 1,
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "booster": trial.suggest_categorical("booster", ["gbtree","gblinear", "dart"]), 
            "lambda": trial.suggest_loguniform("lambda", 1e-2, 10),              
            "alpha": trial.suggest_loguniform("alpha", 1e-2, 10),}               

        if param["booster"] == "gbtree" or param["booster"] == "dart":
            param["max_depth"] = trial.suggest_int("max_depth", 1, 15)  
            param["eta"] = trial.suggest_loguniform("eta", 1e-2, 5)     
            param["gamma"] = trial.suggest_loguniform("gamma", 1e-2, 5) 
            param["grow_policy"] = trial.suggest_categorical("grow_policy", ["depthwise", "lossguide"])  
        if param["booster"] == "dart":
            param["sample_type"] = trial.suggest_categorical("sample_type", ["uniform", "weighted"])
            param["normalize_type"] = trial.suggest_categorical("normalize_type", ["tree", "forest"])
            param["rate_drop"] = trial.suggest_loguniform("rate_drop", 1e-3, 1.0)
            param["skip_drop"] = trial.suggest_loguniform("skip_drop", 1e-3, 1.0)

        
        pruning_callback = optuna.integration.XGBoostPruningCallback(trial, "validation-auc")
        bst = xgboost.train(param, dtrain, evals=[(dtest, "validation")], callbacks=[pruning_callback])
        preds = bst.predict(dtest)
        pred_labels = np.rint(preds)
        accuracy = accuracy_score(y_test, pred_labels)
        
        return accuracy
      
    return objectiveXgboost

def optunaXGBOOST(X,y,size,random):
    '''
    Optimiza todos los parametros de las funciones anteriores.
    Args:
        X : Variable X
        y : Variable target
        size : tamaño del test
        random : numero de random state.
    '''

    objective=XgBoost_X_y(X,y,size,random)
    study = optuna.create_study(direction="maximize")
    study.optimize(objective,n_trials=150)                      
    trial = study.best_trial

    params = []

    for key, value in trial.params.items():
        params.append(value)
        print("    {}: {}".format(key, value))                  
    fig = optuna.visualization.plot_param_importances(study)
    fig.show()
    
    return ()

def omar():
    '''
    This functions shows the 1% world IQ character.
    '''
    urllib.request.urlretrieve("https://media-exp1.licdn.com/dms/image/C4E03AQH9NsUvxFQggA/profile-displayphoto-shrink_800_800/0/1575987701586?e=1656547200&v=beta&t=DM8kWl83h9U6nsRzt3_jqE3b13JjzRljAE6CWVkSNCk", "omar.png")     
    img = Image.open("omar.png")
    img.show()
    
    return ()

def scores(modelo, X_test, y_test, prediction):
    '''
    Función para generar un dataframe con los resultados obtenidos.
    Hay que tener un modelo entrenado y el ".predict" hecho.
    Argumentos:
        modelo : Se trata del nombre del modelo entrenado
        X_test : porción de los datos divididos (variables independientes del modelo) para realizar el test
        y_test (np.array) : porción de los datos divididos (variable target, a predecir o dependiente) para realizar el test
        prediction (np.array) : predicciones calculadas con el modelo entrenado
        
    Retornos:
        DataFrame: DataFrame con los resultados de las métricas MAE, MSE, RMSE y SCORE.
    '''
    resultados = {'LRegression': [
                    mean_absolute_error(y_test, prediction),
                    mean_squared_error(y_test, prediction),
                    np.sqrt(mean_squared_error(y_test, prediction)),
                    modelo.score(X_test, y_test) 
                    ]}

    resultados = pd.DataFrame(resultados, index=['MAE','MSE','RMSE', 'Score'])
    return resultados

def similarity_index(df_col=np.array, cons=float, exp=0.8):
    '''
    Función que genera un valor de similitud estadístico a partir del indice de similitud de
    Bray_Curtis.
    
    Argumentos:
        df_col (np.array): Columna a aplicar la funcion (Columna de pandas).
        cons (float): Valor constante de elemento cuya similitud versus la columna queremos conocer.
        exp (float): Exponente pesado de cada propedad entre número de propiedades, valores entre 0 y 1 (default = 0.8).
    Retornos:
        pandas.Series: Valor de similitud estadístico.
    '''
    sim = df_col.apply(lambda x: (1 - abs((x - cons)/(x + cons)))**exp)
    return sim

def step_axis(init_val=float, num_vals=float, steps=float):
    '''
    Función que generá un array de elementos separados por un valor constante que servirían como eje de gráfico.
    
    Argumentos:
        init_val (float): Valor inicial, donde comenzará el eje.
        num_vals (float): Número de valores que tendrá el array.
        steps (float): Cada cuanto se obtiene valor.
        
    Retornos:
        np.array: array de ejes
    '''
    axis = init_val + np.arange(num_vals)*steps
    return axis

def percentil(data, nivel):
    '''
    Función para saber los percentiles del dataframe
    Argumentos:
        data (pandas.DataFrame) Dataframe.
        nivel (int o float) Nivel del percentil que quieres. Valores entre 0 a 100
    Retornos:
        list: Los limites superiores e inferiores
    '''
    # Límites superior e inferior por percentiles
    superior = np.percentile(data, 100 - nivel)
    inferior = np.percentile(data, nivel)
    # Devuelve los límites superior e inferior
    return [inferior, superior]

def metodo_iqr(data):
    '''
    Función que calcula los limites del rango intercuantilico
    Argumentos:
        data: pandas.core.series.Series de (int) o (float)
    Retornos:
        list: Los limites superiores e inferiores
    '''
    try:
        perc_75 = np.percentile(data, 75)
        perc_25 = np.percentile(data, 25)
    except:
        print('Introduce (ints) o (floats)')
        return

    # Cualcular el IQR (Rango intercuantilico)
    rango_iqr = perc_75 - perc_25

    # Obtención del límite inferior y superior
    iqr_superior = perc_75 + 1.5 * rango_iqr
    iqr_inferior = perc_25 - 1.5 * rango_iqr

    # Devuelve los límites superior e inferior
    return [iqr_inferior, iqr_superior]

def metodo_std(data):
    '''
    Función para saber los limites con la desviacion estandar
    Argumentos:
        data: pandas.core.series.Series de (int) o (float)
    Retornos:
        list: Los limites superiores e inferiores
    '''
    try:      
        std = np.std(data)
    except:
        print('Introduce (ints) o (floats)')
        return

    # Creación de tres desviaciones estándar fuera de los límites
    superior_3std = np.mean(data) + 3 * std
    inferior_3std = np.mean(data) - 3 * std
    # Devuelve los límites superior e inferior
    return [inferior_3std, superior_3std]

def DF_Feature_importance(modelo, X):
    '''
    Función para obtener un data frame con las feature importance de un determinado modelo.
    Argumentos:
        modelo: Model del cual se quiere obtener la visualización de las feature importance
        X: (pandas.DataFrame) variable previamente creada que englobe todas las features del modelo (a excepción de la feature a predecir).
    Retornos:
        pandas.DataFrame: DataFrame con las feature importance del modelo.
    '''
    try:
        X = pd.DataFrame(X)
    except:
        pass

    features_importances_model= pd.DataFrame(modelo.feature_importances_.round(3),
    X.columns, 
    columns = ["Feature importance"]).sort_values("Feature importance", ascending=False)

    return features_importances_model

def preprocess_reviews(reviews):
    '''
    Función que nos prepara el texto eliminando mayusculas,comas y signos.
    Args: Texto que queremos limpiar
    Return: Texto limpio
    
    '''
    REPLACE_NO_SPACE = re.compile("(\.)|(\;)|(\:)|(\!)|(\?)|(\,)|(\")|(\()|(\))|(\[)|(\])|(\d+)")
    REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")
    NO_SPACE = ""
    SPACE = " "
    
    reviews = [REPLACE_NO_SPACE.sub(NO_SPACE, line.lower()) for line in reviews]
    reviews = [REPLACE_WITH_SPACE.sub(SPACE, line) for line in reviews]
    
    return reviews

def remove_stop_words(text,lenguage):
    '''
    Función que elimina stopwords del idioma seleccionado.
    Args: 
        Texto e idioma.
    Return: 
        Texto limpio.
    '''
    english_stop_words = stopwords.words(lenguage)

    removed_stop_words = []
    for review in text:
        removed_stop_words.append(
            ' '.join([word for word in review.split() if word not in english_stop_words])
        )
    return removed_stop_words
    
def sweet_table(X_test, y_test, *arbitrarios):
   '''
    Nos proporciona una pequeña descripción de las principales métricas a utilizar par evaluar el rendimiento
    de nuestro modelo de ML. Nota: los modelos pasados deben tener las mismas features.
    Siempre y cuando se siga el siguiente proceso: 
    1) X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)
    2) Con nuestro modelo definido (ejemplo):
       model = LGBMRegressor()
       model1 = LinearRegression()
    3) Entrenado nuestro modelo:
       model.fit(X_train, y_train)
       model1.fit(X_train, y_train)
    Argumentos:
      X_test (np.array): (Ver Descripción)
      y_test (np.array): (Ver Descripción)
      *arbitrareos (str): Serán uno o varios algoritmos con los que se quiere entrenar y evaluar nuestro modelo de ML.
   '''

   names = ['Metrics']
   maes = ['mae']
   mses = ['mse']
   rmses = ['rmse']
   score_test = ['Accuracy (r2_score)']
   # score_train = ['Accuracy (TRN)']
   # mean_rmses = ['Mean(RMSE)_CrossValidation']
   for model in arbitrarios:
      names.append(str(model))
      MAE = mean_absolute_error(y_test, model.predict(X_test))
      maes.append(str(MAE))
      MSE = mean_squared_error(y_test, model.predict(X_test))
      mses.append(str(MSE))
      RMSE = np.sqrt(mean_squared_error(y_test, model.predict(X_test)))
      rmses.append(str(RMSE))
      ACC =  r2_score(y_test, model.predict(X_test))
      score_test.append(str(ACC))
      # SCORE_TR = model.score(X_train, y_train)
      # SCORE_TS = model.score(X_test, y_test)
   x = PrettyTable()
   x.field_names = names
   x.add_row(maes)
   x.add_row(mses)
   x.add_row(rmses)
   x.add_row(score_test)
   # x.add_row(score_train)
   # x.add_row(mean_rmses)

   return x

def check_optimizadores (modelo, optimizadores, epochs, loss, metrics, x_data, y_data, bath, callbks):
    
    
    ''' Funcion que compila y entrena un modelo con uno o varios optimizadores, a través de un bucle for y muestra dos graficos.
    graf_df_result = df_results.plot.bar() muestra la funcion de perdida, tanto para train como para la parte de validacion.
    graf_epoc muestra como han ido convergiendo el modelo con cada uno de los optimizadores, tanto para el train como
    para la validadcion.   
    
    INPUT:
    modelo (objeto keras.engine.): modelo con las capas ya definidas fuera de la funcion
    optimizadores (lista): lista con el/los optimizadores que se vayan a entrenar
    epochs (int): entero con el número de epocs
    loss (str): funcion loss que se va a fijar
    metrics (objeto keras.metrics): metrica que se va a utilizar para el entrenamiento
    x_data (np.array): los datos de train para el entrenamiento
    xy_data (np.array): los datos de la variable a predecir para el entrenamiento
    bath (int): numero de paquetes o muestras para calcular el error.
    callbaks (lista): lista con las callbacks que se van a quere utilizar en el modelo
    
   
    
    '''
    
    results = {}
    history = {}

    for optimizadores in optimizadores:
    
  
    
        modelo.compile (loss = loss, optimizer= optimizadores, metrics = metrics)
        optimizer_key = str(type(optimizadores).__name__)
        history[optimizer_key] = modelo.fit(x_data, y_data, batch_size = bath, epochs = int(epochs), validation_split = 0.2,callbacks= callbks)
        results[optimizer_key] = {}
        results[optimizer_key]['loss'] = history[optimizer_key].history['loss'][epochs -1]
        results[optimizer_key]['val_loss'] = history[optimizer_key].history['val_loss'][epochs -1]
        
        df_results = pd.DataFrame(results)
    graf_df_result = df_results.plot.bar()
    plt.show()
    
    graf_epoc = plt.figure(figsize= (7,7))
    plt.xlabel ('Epoch')
    plt.ylabel('Loss')
    
    for optimizadores in history:
        hist = pd.DataFrame(history[optimizadores].history)
        
        plt.plot(history[optimizadores].epoch, np.array(hist['loss']),
                label = 'Train loss' + optimizadores)
        plt.plot(history[optimizadores].epoch, np.array(hist['val_loss']),
                label = 'Val loss' + optimizadores)
    plt.legend()
    plt.show()
    
    return graf_df_result, graf_epoc  

