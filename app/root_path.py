from dotenv import load_dotenv
import os

load_dotenv()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print('root path is: ' + ROOT)
