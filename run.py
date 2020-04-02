import re
import sys
import time
import json
from git import Repo

# ------------------------------------------------------------------------------

def encode_commit(info, c, branch):

    # in-place create ahref tags for JIRA
    txt = c.message
    if info['jira_link']:
        txt = re.sub(r'(SW-\d+)', r'<a href=' + info['jira_link'] + r'\1>\1</a>', txt)

    j = {
        'id': c.hexsha,
        'message': txt,
        'name': c.author.name,
        'email': c.author.email,
        'authored_date': c.authored_date,
        'committed_date': c.committed_date,
        'total': c.stats.total,
        'files': c.stats.files,
        'idlink': info['cid_link'] + c.hexsha,
        'branch': branch,
    }
    return j

def process_repo(info):

    tnow = time.time()

    print("processing repo", info['local_path'])
    repo = Repo(info['local_path'])
    assert not repo.bare, "trouble loading " + info['local_path']

    # update the repo. NOTE: does not seem to work sometimes? doing manually for now. debug later
    # print("pulling the latest...")
    # o = repo.remotes.origin
    # o.pull()

    # fetch active branches and extract the time of latest commit to each branch
    print("fetching active branches...")
    refs = sorted(repo.refs, key=lambda r: r.commit.authored_date, reverse=True)
    refs = [r for r in refs if (tnow - r.commit.authored_date)/60/60/24 < info['dtmax']]
    print("found %d branches with new commits" % (len(refs), ))

    # get all commits on branches
    print("extracting all commits...")
    have = set()
    commits = []
    for r in refs:
        n = 0
        for c in repo.iter_commits(r.name):
            if (tnow - c.authored_date)/60/60/24 > info['dtmax']:
                continue # skip very old commits
            h = c.hexsha
            if not h in have:
                n += 1
                have.add(h)
                encoded = encode_commit(info, c, r.name)
                if not 'Automatic merge from' in encoded['message']:
                    commits.append(encoded)
        if n > 0:
            print(r.name, n)
    commits.sort(key=lambda r: r['authored_date'], reverse=True)

    out = {
        'commits': commits,
        'dtmax': info['dtmax']
    }
    return out

# ------------------------------------------------------------------------------
if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--repos-config', help='configuration json file of repos to use')
    args = parser.parse_args()

    with open(args.repos_config, 'r') as f:
        config = json.load(f)
        infos = config['infos']

    # process each one in turn
    for info in infos:
        jout = process_repo(info)
        # write JSON output
        out_path = 'deploy/%s.json' % (info['name'], )
        with open(out_path, 'w') as f:
            json.dump(jout, f)
        print("wrote", 'deploy/%s.json' % (info['name'], ))
