#!/usr/bin/env python

from pyod.models.ecod import ECOD as _ECOD

from codec import codecs_manager
from base import BaseAlgo, ClustererMixin
from models.base import save_model
from util import df_util
from util.param_util import convert_params
from cexc import get_messages_logger,get_logger
import datetime

class ECOD(ClustererMixin, BaseAlgo):

    def __init__(self, options):

        self.handle_options(options)

        out_params = convert_params(
            options.get("params", {}),
            floats=["contamination"]
        )
        self.estimator = _ECOD(**out_params)

    def fit(self, df, options):

        # Create a copy of the dataframe so we do not alter the original
        X = df.copy()


        # Use the utility function from Splunk to prepare the training dataset
        X, nans, _ = df_util.prepare_features(
            X=X,
            variables=options.get("feature_variables"),
            get_dummies=False,
            mlspl_limits=options.get("mlspl_limits"),
        )
        
        # Fit the ECOD classifier on the training dataset
        self.estimator.fit(X.values)

        # Merge the predictions with the anomaly scores
        y_hat = list(zip(self.estimator.labels_, self.estimator.decision_scores_))

        # Prepare the output dataframe by using the utility function from Splunk
        output = df_util.create_output_dataframe(
            y_hat=y_hat, nans=nans, output_names=["isOutlier", "anomaly_score"]
        )

        # Merge the original dataframe with the predictions
        df = df_util.merge_predictions(df, output)

        return df

    def apply(self, df, options):

        # Create a copy of the dataframe so we do not alter the original
        X = df.copy()

        # Use the utility function from Splunk to prepare the inference dataset
        X, nans, _ = df_util.prepare_features(
            X=X,
            variables=options.get("feature_variables"),
            get_dummies=False,
            mlspl_limits=options.get("mlspl_limits"),
        )

        # Predict the inference dataset with the trained ECOD clsasifier and convert the integer results to strings
        y_hat = self.estimator.predict(X.values)
        y_hat = y_hat.astype("str")

        # Save the anomaly scores
        anomaly_scores = self.estimator.decision_function(X)

        # Merge the predictions with the anomaly scores
        y_hat = list(zip(y_hat, anomaly_scores))

        # Prepare the output dataframe by using the utility function from Splunk
        output = df_util.create_output_dataframe(
            y_hat=y_hat, nans=nans, output_names=["isOutlier", "anomaly_score"]
        )

        # Merge the original dataframe with the predictions
        df = df_util.merge_predictions(df, output)

        return df

    @staticmethod
    def register_codecs():
        from codec.codecs import SimpleObjectCodec
        codecs_manager.add_codec("algos_contrib.ECOD", "ECOD", SimpleObjectCodec)
        codecs_manager.add_codec("pyod.models.ecod", "ECOD", SimpleObjectCodec)
