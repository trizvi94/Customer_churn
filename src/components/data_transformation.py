import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object
import os

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path=os.path.join('artifacts',"preprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformationConfig()

    def get_data_tranformer_object(self):
        '''
        This func is responsible for data tranmsformation
        '''

        try:
            categorical_features = ['Geography', 'Gender']
            numeric_features = ['CreditScore', 
                                'Age', 
                                'Tenure',
                                'Balance', 
                                'NumOfProducts', 
                                'HasCrCard', 'IsActiveMember', 'EstimatedSalary']
            num_pipeline= Pipeline(
                steps=[
                    ("scaler",StandardScaler())
                ]
            
            )
            cat_pipeline= Pipeline(
                steps=[
                    ("one_hot_encoder",OneHotEncoder()),
                    ("scaler",StandardScaler(with_mean=False))
                ]
                
            )
            logging.info(f"Numerical Columns: {numeric_features}")
            logging.info(f"Categorical Columns:{categorical_features}")

            preprocessor=ColumnTransformer(
                [
                   ( "num_pipeline",num_pipeline,numeric_features),
                   ("cat_pipeline",cat_pipeline,categorical_features)
                ]
            )
            return preprocessor
        except Exception as e:
            raise CustomException(e,sys)
        
    
    def initiate_data_transformation(self,train_path,test_path):
        try:
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info("Read train and test Data")

            logging.info("Obtaining preprocessing object")

            preprocessing_obj=self.get_data_tranformer_object()
            target_column_name='Exited'
            categorical_features = ['Geography', 'Gender']
            numeric_features = ['CreditScore', 
                                'Age', 
                                'Tenure',
                                'Balance', 
                                'NumOfProducts', 
                                'HasCrCard', 'IsActiveMember', 'EstimatedSalary']
            
            input_feature_train_df=train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df=train_df[target_column_name]

            input_feature_test_df=test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df=test_df[target_column_name]

            logging.info(
                f"Applying preprocessing object on training dataframe and testing dataframe." )

            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)

            train_arr = np.c_[
                input_feature_train_arr, np.array(target_feature_train_df)
            ]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info(f"Saved preprocessing object.")

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj
            )

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )
        except Exception as e:
            raise CustomException(e,sys)