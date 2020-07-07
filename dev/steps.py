#!/usr/bin/env python3
def steps():
	steps= """
# create structure
mkdir -p /data/wrk/{app_name}[0]/{app_name}/1/src
cd /data/wrk/{app_name}[0]/{app_name}/1/src

# setup git
gitframe --init . ../doc ../mgt --username user --email user@email.com
gitframe --clone-to-repository . ../doc ../mgt --repository /data/git --package {app_name} --add-origin --sync
release --set-conf
gitframe --open-branch  #features branch
# add files, could be just one step with create structure by importing a template.
echo -e ".git" > .refine
release --set-launcher

# release work
release --bump-version --increment
gitframe --tag --version-file gpm.json
release --export-rel
release --export-bin --beta

##  update gitframe
cd /data/wrk/g/gitframe/1/src/
main.py --clone-to-repository . ../doc ../mgt --repository /data/git --package options --add-origin --sync
release --bump-version --increment
main.py --update-gitframe; gitframe --tag --version-file gpm.json
release --export-rel

## update release
cd /data/wrk/r/release/1/src
main.py --export-bin --beta; release --set-launcher
release --bump-version --increment
gitframe --tag --version-file gpm.json
gitframe --clone-to-repository . ../doc ../mgt --repository /data/git --package release --add-origin --sync
main.py --export-bin --beta && release --export-rel && release --export-bin
main.py --bump-version --increment && gitframe --tag --version-file gpm.json && release --export-rel && release --export-bin

## import a template
release -i -p template-py --no-conf-src --no-conf-dst --no-root-dir --not-git --path-deps .
rm -rf /home/gabaaa/Desktop/test/{,.[!.],..?}*; /data/wrk/r/release/1/src/main.py -i -p template-py --no-conf-src --no-conf-dst --no-root-dir --not-git --path-deps . --keys
rm -rf /home/gabaaa/Desktop/test/{,.[!.],..?}*; release -i -p template-py --no-conf-src --no-conf-dst --no-root-dir --not-git --path-deps . --keys "{'authors': 'John Doe', 'licenses': 'MIT', 'version':'0.2.0', 'package_name': 'mytestpackage'}"







# # # # sshk
# # # # gf --anp
# # # # # Enter repository [q to quit]: git@domain:/apps/a/{app_name}/1     │
# # # # # Server Password:                                                                 │
# # # # # Enter git user email [q to quit]: user@domain                            │
# # # # # Enter ssh user [q to quit]: user  

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
