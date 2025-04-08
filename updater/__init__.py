import os
import hashlib
from pathlib import Path
from customizer.customize import Customizer
from utils.db import JotunDBUtils
from sqlite3 import Error
from typing import Union
from tabulate import tabulate