#!/usr/bin/bash
git add *
git commit
branch_name=$(git symbolic-ref -q HEAD) || branch_name="(unnamed branch)"
branch_name=${branch_name##refs/heads/}
git push -u origin ${branch_name}
