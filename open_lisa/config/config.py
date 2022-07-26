from dotenv import load_dotenv
import os
import logging


def load_config(env):
    cfg_path = os.path.join(os.path.dirname(__file__), "{}.env".format(env))
    logging.info(
        "[OpenLISA][load_config] - Loading env variables from {}".format(cfg_path))
    load_dotenv(cfg_path)
