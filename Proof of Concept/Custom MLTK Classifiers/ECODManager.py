#!/usr/bin/env python

from pyod.models.ecod import ECOD as _ECOD

from codec import codecs_manager
from base import BaseAlgo, ClustererMixin
from util import df_util
from util.param_util import convert_params
from cexc import get_messages_logger, get_logger
from codec import MLSPLEncoder, MLSPLDecoder
from util.models_util import load_algo_options_from_disk
from algos_contrib.ECOD import ECOD
from distutils.version import StrictVersion
import pandas as pd 
import numpy as np
import os
import csv
import json
import datetime

class ECODManager(ClustererMixin, BaseAlgo):

    def __init__(self, options):

        self.handle_options(options)

        self.out_params = convert_params(
            options.get("params", {}),
            floats=["contamination"],
            bools=["mgr_training", "mgr_save"],
            strs=["mgr_model_dir"]
        )

        if "contamination" in self.out_params and not (0.0 < self.out_params["contamination"] <= 0.5):
            msg = "Invalid value error: Valid values for contamination are in (0.0, 0.5], but found contamination='{}'."
            raise RuntimeError(msg.format(self.out_params["contamination"]))

        if "mgr_save" not in self.out_params:
            msg = "Must provide mgr_save."
            raise RuntimeError(msg)
        
        if "mgr_training" not in self.out_params:
            msg = "Must provide mgr_training."
            raise RuntimeError(msg)

        if "mgr_model_dir" not in self.out_params:
            msg = "Must provide mgr_model_dir."
            raise RuntimeError(msg)

    def fit(self, df, options):

        ECOD.register_codecs()

        # Remove all parameters that are destined for the manager class
        ecod_options= options.copy()
        ecod_options["params"] = {k: v for k, v in options["params"].items() if not k.startswith("mgr_")}
        
        # Group the search results by users
        grouped = df.groupby("user", as_index=False)

        # Output dataframe
        all_results = pd.DataFrame()

        model_dir = self.out_params["mgr_model_dir"]
        
        for group_name, group_df in grouped:

            file_path = os.path.join(model_dir, f"{group_name}.mlmodel")

            # If a model exists, deserialize it and apply it on the group dataframe
            if not self.out_params["mgr_training"] and os.path.exists(file_path):
                _, model_data, model_options = load_algo_options_from_disk(file_path=file_path)
                clf = decode(model_data["model"])
                results = clf.apply(group_df, model_options)
                all_results = pd.concat([all_results, results])
                continue

            # Train the ECOD classifier on the group dataframe and optionally save it
            clf = ECOD(options=ecod_options)
            results = clf.fit(df=group_df, options=ecod_options)
            all_results = pd.concat([all_results, results])
            if self.out_params["mgr_save"]:
                save_model(clf, model_dir, group_name, ecod_options)

        return all_results


def save_model(clf, model_dir, name, options):
    opaque = encode(clf)
    os.makedirs(model_dir, mode=0o770, exist_ok=True)
    file_path = os.path.join(model_dir, f"{name}.mlmodel")
    with open(file_path, mode="w") as f:
        model_writer = csv.writer(f)
        model_writer.writerow(["algo", "model", "options"])
        model_writer.writerow(["ECOD", opaque, json.dumps(options)])


def encode(obj):
    if StrictVersion(np.version.version) >= StrictVersion('1.10.0'):
        return MLSPLEncoder().encode(obj)
    else:
        raise RuntimeError(
            'Python for Scientific Computing version 1.1 or later is required to save models.'
        )


def decode(payload):
    if StrictVersion(np.version.version) >= StrictVersion('1.10.0'):
        return MLSPLDecoder().decode(payload)
    else:
        raise RuntimeError(
            'Python for Scientific Computing version 1.1 or later is required to load models.'
        )