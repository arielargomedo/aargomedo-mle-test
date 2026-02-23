import pandas as pd
import numpy as np
from typing import Tuple, Union, List
from datetime import datetime

from sklearn.linear_model import LogisticRegression

class DelayModel:

    def __init__(
        self
    ):
        self._model = None # Model should be saved in this attribute.

    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """
        data = data.copy()
        data = self._add_features(data)

        # One-hot encoding SOLO para las columnas esperadas
        X = pd.concat([
            pd.get_dummies(data["OPERA"], prefix="OPERA"),
            pd.get_dummies(data["TIPOVUELO"], prefix="TIPOVUELO"),
            pd.get_dummies(data["MES"], prefix="MES"),
        ], axis=1)

        # Columnas exactas que espera el test
        FEATURES_COLS = [
            "OPERA_Latin American Wings", 
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air"
        ]

        # Asegurar que existan todas
        for col in FEATURES_COLS:
            if col not in X.columns:
                X[col] = 0

        # Orden correcto
        X = X[FEATURES_COLS]

        if target_column:
            y = data[[target_column]]
            return X, y

        return X

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """
        self._feature_columns = features.columns.tolist()
        
        self._model = LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            random_state=42
        )

        self._model.fit(features, target)

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """

        if self._model is None:
            return [0] * len(features)
        
        features = features[self._feature_columns]
        predictions = self._model.predict(features)

        return predictions.astype(int).tolist()

    def _add_features(self, data, threshold=15):
        if "Fecha-I" in data.columns and "Fecha-O" in data.columns:
            # Add feature period_day
            def get_period_day(date):
                date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').time()
                morning_min = datetime.strptime("05:00", '%H:%M').time()
                morning_max = datetime.strptime("11:59", '%H:%M').time()
                afternoon_min = datetime.strptime("12:00", '%H:%M').time()
                afternoon_max = datetime.strptime("18:59", '%H:%M').time()
                evening_min = datetime.strptime("19:00", '%H:%M').time()
                evening_max = datetime.strptime("23:59", '%H:%M').time()
                night_min = datetime.strptime("00:00", '%H:%M').time()
                night_max = datetime.strptime("4:59", '%H:%M').time()
                
                if(date_time > morning_min and date_time < morning_max):
                    return 'mañana'
                elif(date_time > afternoon_min and date_time < afternoon_max):
                    return 'tarde'
                elif(
                    (date_time > evening_min and date_time < evening_max) or
                    (date_time > night_min and date_time < night_max)
                ):
                    return 'noche'
                
            # Add feature high_season
            def is_high_season(fecha):
                fecha_año = int(fecha.split('-')[0])
                fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
                range1_min = datetime.strptime('15-Dec', '%d-%b').replace(year = fecha_año)
                range1_max = datetime.strptime('31-Dec', '%d-%b').replace(year = fecha_año)
                range2_min = datetime.strptime('1-Jan', '%d-%b').replace(year = fecha_año)
                range2_max = datetime.strptime('3-Mar', '%d-%b').replace(year = fecha_año)
                range3_min = datetime.strptime('15-Jul', '%d-%b').replace(year = fecha_año)
                range3_max = datetime.strptime('31-Jul', '%d-%b').replace(year = fecha_año)
                range4_min = datetime.strptime('11-Sep', '%d-%b').replace(year = fecha_año)
                range4_max = datetime.strptime('30-Sep', '%d-%b').replace(year = fecha_año)
                
                if ((fecha >= range1_min and fecha <= range1_max) or 
                    (fecha >= range2_min and fecha <= range2_max) or 
                    (fecha >= range3_min and fecha <= range3_max) or
                    (fecha >= range4_min and fecha <= range4_max)):
                    return 1
                else:
                    return 0
            
            # Add feature min_diff
            def get_min_diff(data):
                fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
                fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
                min_diff = ((fecha_o - fecha_i).total_seconds())/60
                return min_diff
            
            # Modify columns 
            data['period_day'] = data['Fecha-I'].apply(get_period_day)
            data['high_season'] = data['Fecha-I'].apply(is_high_season)
            data['min_diff'] = data.apply(get_min_diff, axis = 1)

        threshold_in_minutes = threshold
        if "min_diff" in data.columns:
            data['delay'] = np.where(data['min_diff'] > threshold_in_minutes, 1, 0)

        return data