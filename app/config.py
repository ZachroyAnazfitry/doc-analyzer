"""App configuration from environment with defaults."""
import os

MODEL_NAME = os.getenv("MODEL_NAME", "sshleifer/distilbart-cnn-6-6")
MAX_LENGTH = int(os.getenv("MAX_LENGTH", "130"))
MIN_LENGTH = int(os.getenv("MIN_LENGTH", "30"))
