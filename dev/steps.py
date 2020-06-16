#!/usr/bin/env python3
def steps():
	steps= """
mkdir -p /data/wrk/a/{app_name}/1
cd /data/wrk/a/{app_name}/1
sshk
gf --anp
# Enter repository [q to quit]: git@domain:/apps/a/{app_name}/1     │
# Server Password:                                                                 │
# Enter git user email [q to quit]: user@domain                            │
# Enter ssh user [q to quit]: user  
release --set-bump-deploy
sj --so {app_name}
gf -o #features branch

release --set-conf

# add files
.gitignore
__pycache__/
.env/
.pytest_cache/
.vscode
*.pyc
modules/
gpkgs/

## if existing folder:
git checkout develop
git merge release-1.0.0
git branch --delete release-1.0.0
git push origin --delete release-1.0.0
gf -o # features branch 'at work'

for gitignore:
	git rm -r --cached . 
	git add .

## create __init__.py:

#!/usr/bin/env python3
# author: {author}
# version: {version}
# name: {app_name}
# license: {licence}
__version__ = "{version}"

## create main.py, or test.py
#!/usr/bin/env python3
# author: {author}
# version: {version}
# name: {app_name}
# license: {licence}

if __name__ == "__main__":
    import sys, os
    import importlib
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]
			
## .refine
__pycache__/
.env/
.pytest_cache/
.vscode
.git/
.gitignore
/archives/
		dev files

## add headers to them
#!/usr/bin/env python3
# author: {author}
# version: {version}
# name: {app_name}
# license: {licence}

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
