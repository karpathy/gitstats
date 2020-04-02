# gitstats

Reads any git repository and produces a nice and colorful summary for all of ongoing work in the repository, and convenient links to JIRA/BitBucket etc.

To get working:

1. create a repos json configuration file by following the example in example_repos.json
2. cd into the git repo of interest and git pull
3. run `run.py` to process all the commits and write json files of output to `deploy/` directory
4. `cd deploy`
5. `python -m http.server`
6. visit the web browser
7. open up the console and issue `load_json("output.json");` where you point to the json file produced by run. LOL. ok need to make this better in the future obviously.
