# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
from KDEpy import NaiveKDE


def execute_custom_KDE(data: pd.Series, bandwidth: (int | str)) -> (pd.Series | None):
    try:
        kde = NaiveKDE(kernel='gaussian', bw=bandwidth).fit(np.array(data))
    except Exception:
        kde = None
    return kde

def calculate_custom_bandwidth(data: pd.Series) -> (float | None):
    try:
        custom_bandwidth = data[data > 0].mode().min() / 2
    except ValueError:
        custom_bandwidth = None
    return custom_bandwidth


class SequentialOutlierDetector():

    def __init__(self):
        self._labels = None

    def add_NaNs(self, nan_df_index: pd.DataFrame.index) -> None:
        self._labels = pd.Series(index=nan_df_index)
        self._labels[:] = pd.NA

    def add_cluster_labels(self, labeled_data: pd.Series) -> None:
        self._labels = pd.concat([self._labels, labeled_data]) 

    # This algorithm assumes there are no missing indices

    def detect_outliers(self, kernel_size: int = 2, outlier_cluster_label=1) -> None: 
        if kernel_size > 2:
            raise ValueError("Time series analysis with an outlier kernel not equal to 2 is currently not supported")
        detected_outliers_mask = pd.Series(index=self._labels.index)
        detected_outliers_mask[:] = False
        detected_outliers_mask[self._labels.isna()] = True
        outlier_sums = self._labels[:].fillna(outlier_cluster_label).rolling(kernel_size).sum()

        #adjust index due to rolling sums
        adjust_index_offset = -1
        outliers = outlier_sums[outlier_sums == 2]
        detected_outliers_mask.iloc[outliers.index + adjust_index_offset] = True
        # the first sum is always nan. Check the second (1) and see if its 1 and if so its an outlier
        if self._labels.iloc[1] == 1:
            detected_outliers_mask.iloc[0] = True
        # if final label is 1 then the final index is the outlier not the second to least index
        if self._labels.iloc[-1] == 1:
            detected_outliers_mask.iloc[-1] = True
        return detected_outliers_mask
    

class OutlierClassifier():

    def KDE(self, df, column_name: str) -> pd.Series:
        nan_delta = df.delta(column_name, drop_first_row=False)
        delta = nan_delta.dropna()
        kde = execute_custom_KDE(delta, 'ISJ')
        if kde == None:
            custom_bandwidth = calculate_custom_bandwidth(delta)
            if custom_bandwidth != None: 
                kde = execute_custom_KDE(delta, custom_bandwidth)
        if kde == None:
            kde = execute_custom_KDE(delta, 1)
        if kde == None:
            raise IOError(f"KDE was not generated for attribute: {column_name}")

        # Get KDE score for each delta
        kde_scores = kde.evaluate(np.array(delta))

        # Cluster the deltas on their density score into two groups
        kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(kde_scores)
        clusters = np.abs(kmeans.labels_ - 1)
        clusters = np.insert(clusters, 0, -1)
        classification = pd.Series(clusters, index=nan_delta.index)
        return classification       





    