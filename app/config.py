import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "..", "environment.ini"))

MONITORING_SERVICE_URL = config["DEFAULT"].get(
    "MONITORING_SERVICE_URL", "http://host.docker.internal:10303/api/heartbeat"
)
COMPUTE_ID = config["DEFAULT"].get("COMPUTE_ID", "compute-001")
INTERVAL_SECONDS = config["DEFAULT"].getint("INTERVAL_SECONDS", 60)


AWS_ACCESS_KEY_ID = config["aws"]["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = config["aws"]["AWS_SECRET_ACCESS_KEY"]
S3_BUCKET_NAME = config["aws"]["S3_BUCKET_NAME"]
S3_UPLOAD_PREFIX = config["aws"].get("S3_UPLOAD_PREFIX", "checkpoints")
