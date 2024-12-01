import os
import warnings
from dotenv import load_dotenv

def initialize_env():
    load_dotenv()
    warnings.filterwarnings("ignore")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "Apsara 2.0"