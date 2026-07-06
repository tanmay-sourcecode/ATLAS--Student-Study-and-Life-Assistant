import os
import sys
import logging
import warnings
from dotenv import load_dotenv

# Add parent directory to sys.path so that absolute imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load env variables from root folder
load_dotenv(os.path.join(project_root, ".env"))

# Suppress warnings and standard ADK logs
warnings.simplefilter("ignore", UserWarning)
logging.getLogger("google_adk").setLevel(logging.CRITICAL)
logging.getLogger("google_adk").propagate = False

# Import the existing orchestrator agent and expose it as root_agent
from orchestrator.agent import orchestrator_agent

root_agent = orchestrator_agent
