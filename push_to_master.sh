#!/usr/bin/env bash

cp modoverridesGen.py /tmp/modoverridesGen.py

git checkout master
git pull -r

cp /tmp/modoverridesGen.py modoverridesGen.py

git add modoverridesGen.py
git commit --message="update modoverridesGen.py"
git push

git checkout -