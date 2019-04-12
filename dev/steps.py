#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.1.2
# name: gpm
# license: MIT

import os
from pprint import pprint
import re
import glob
import shutil

def steps():
	steps= """
		create folder
		gf --anp
			user@domain:/apps/f/{app_name}/_1/{app_name}/
		release --set-bump-deploy
		sj --so {app_name}

		gf -o #features branch

		gpm --init --no-db

		add files
			.gitignore
__pycache__/
.env/
.pytest_cache/
.vscode
*.pyc
modules/
gpkgs/
			
			.refine
__pycache__/
.env/
.pytest_cache/
.vscode
.git/
.gitignore
/archives/
		dev files

		add headers to them
#!/usr/bin/env python3
# author: Gabriel Auger
# version: 0.1.0
# name: {app_name}
# license: MIT

		create a test.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
try:
    from src import ft
except:
    from format_text import ft
del sys.path[0]

touch .gitignore
touch .refine
mkdir dev
touch __init__.py
chmod +x __init__.py
touch test.py
chmod +x test.py
mkdir gpkgs

		gf --pr

	"""	
	print(steps)
