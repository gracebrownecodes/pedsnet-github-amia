import json
from collections import defaultdict
from github3 import login
from github3.models import GitHubError
import datetime, time
import csv

# Load settings from config file
settings = json.loads(open('./.config.json', 'r').read())

# Get authenticated GitHub session
gh = login(**settings['auth'])

# Get the org object defined in settings
org = gh.organization(settings['org'])

# Week stat factory
def new_week_stats():
    return {
        'commits': 0,
        'commit_comments': 0,
        'code_additions': 0,
        'code_deletions': 0,
        'issues_opened': 0,
        'issues_closed': 0,
        'issue_comments': 0,
        'contributors': [],
        'contributor_count': 0,
    }

# Repo stat factory
def new_repo_stats():
    return {
        'contributors': 0,
        'created_at': '0000-00-00',
        'weeks_old': 0.0,
        'code_additions': 0,
        'additions_per_week': 0.0,
        'code_deletions': 0,
        'deletions_per_week': 0.0,
        'commits': 0,
        'commits_per_week': 0.0,
        'commit_comments': 0,
        'comments_per_commit': 0.0,
        'issues': 0,
        'issues_per_week': 0.0,
        'closed_issues': 0,
        'closed_per_week': 0.0,
        'issue_comments': 0,
        'comments_per_closed': 0.0,
        'contributors_per_week': 0.0,
        'weeks': defaultdict(new_week_stats)
    }

# Initialize stats
stats = {
    'contributors': 0,
    'repo_count': 0,
    'created_at': '0000-00-00',
    'weeks_old': 0.0,
    'repos': defaultdict(new_repo_stats),
    'code_additions': 0,
    'additions_per_week': 0.0,
    'code_deletions': 0,
    'deletions_per_week': 0.0,
    'commits': 0,
    'commits_per_week': 0.0,
    'commit_comments': 0,
    'comments_per_commit': 0.0,
    'issues': 0,
    'issues_per_week': 0.0,
    'closed_issues': 0,
    'closed_per_week': 0.0,
    'issue_comments': 0,
    'comments_per_closed': 0.0,
    'contributors_per_repo': 0.0,
    'contributors_per_week': 0.0,
    'weeks': defaultdict(new_week_stats)
}

isof = '%Y-%m-%d'

def next_week_iso(iso_date):
    date = datetime.datetime.strptime(iso_date, isof).date()
    return (date + datetime.timedelta(days=7)).isoformat()

def last_week_iso(iso_date):
    date = datetime.datetime.strptime(iso_date, isof).date()
    return (date - datetime.timedelta(days=7)).isoformat()

def weeks_old_iso(iso_date, iso_now):
    date = datetime.datetime.strptime(iso_date, isof).date()
    now = datetime.datetime.strptime(iso_now, isof).date()
    return (now - date).days / float(7)

# Get current datetime
now = datetime.date.today().isoformat()

# Get org created datetime, calculate weeks old, and setup weeks dict
stats['created_at'] = org.to_json()['created_at'][:10]
stats['weeks_old'] = weeks_old_iso(stats['created_at'], now)
week_start = stats['created_at']
while week_start < now:
    # Initialize a week stat
    week_stat = stats['weeks'][week_start]
    week_start = next_week_iso(week_start)

# Add up members in the org
for member in org.iter_members():
    stats['contributors'] += 1

# Initialize contributors, the only var that needs to be summed across the org
# and isn't actually tracked on the org.
contributors = 0

for repo in org.iter_repos():
    # Increment repo count
    stats['repo_count'] += 1

    # Initialize repo stats
    repo_stats = stats['repos'][repo.name]

    # Set repo created date, calculate weeks old, and setup weeks dict,
    # using the same week_starts as the org
    repo_stats['created_at'] = repo.to_json()['created_at'][:10]
    repo_stats['weeks_old'] = weeks_old_iso(repo_stats['created_at'], now)
    week_before_created = last_week_iso(repo_stats['created_at'])
    for week_start in stats['weeks'].iterkeys():
        if week_start > week_before_created:
            # Initialize repo week stat
            week_stat = repo_stats['weeks'][week_start]

    # Get number of contributors and add to org-wide count
    for contributor in repo.iter_contributors():
        repo_stats['contributors'] += 1
    contributors += repo_stats['contributors']

    # Get commit numbers, add to appropriate weeks member, calculate commits
    # per week, and add to org stats
    # Simultaneously, get code changes, add to appropriate weeks member,
    # calculate changes per week, and add to org stats
    for commit in repo.iter_commits():
        repo_stats['commits'] += 1
        # Handle ridiculously large commit that causes a 502 error
        if commit.to_json()['url'] == u'https://api.github.com/repos/PEDSnet/StLouis/commits/6b955a37d6b8b00230e9a5871d7e1e4f20ed0f0f':
            repo_stats['code_additions'] += 1875020
            repo_stats['code_deletions'] += 910228
            commit_date = u'2014-09-08'
            commit_author = 'bgkenney'
            for week_start, repo_week_stat in repo_stats['weeks'].iteritems():
                next_week_start = next_week_iso(week_start)
                if week_start <= commit_date < next_week_start:
                    org_week_stat = stats['weeks'][week_start]
                    repo_week_stat['commits'] += 1
                    org_week_stat['commits'] += 1
                    repo_week_stat['code_additions'] += 1875020
                    org_week_stat['code_additions'] += 1875020
                    repo_week_stat['code_deletions'] += 910228
                    org_week_stat['code_deletions'] += 910228
                    if commit_author not in repo_week_stat['contributors']:
                        repo_week_stat['contributors'].append(commit_author)
                        repo_week_stat['contributor_count'] += 1
                    if commit_author not in org_week_stat['contributors']:
                        org_week_stat['contributors'].append(commit_author)
                        org_week_stat['contributor_count'] += 1
            continue
        try:
            commit = repo.commit(commit.sha)
        except GitHubError:
            print commit.to_json()
            raise e
        repo_stats['code_additions'] += commit.additions
        repo_stats['code_deletions'] += commit.deletions
        commit_date = commit.commit.to_json()['author']['date'][:10]
        for week_start, repo_week_stat in repo_stats['weeks'].iteritems():
            next_week_start = next_week_iso(week_start)
            if week_start <= commit_date < next_week_start:
                org_week_stat = stats['weeks'][week_start]
                repo_week_stat['commits'] += 1
                org_week_stat['commits'] += 1
                repo_week_stat['code_additions'] += commit.additions
                org_week_stat['code_additions'] += commit.additions
                repo_week_stat['code_deletions'] += commit.deletions
                org_week_stat['code_deletions'] += commit.deletions
                if commit.author:
                    commit_author = unicode(commit.author.login)
                    if commit_author not in repo_week_stat['contributors']:
                        repo_week_stat['contributors'].append(commit_author)
                        repo_week_stat['contributor_count'] += 1
                    if commit_author not in org_week_stat['contributors']:
                        org_week_stat['contributors'].append(commit_author)
                        org_week_stat['contributor_count'] += 1
                break
    repo_stats['commits_per_week'] = (repo_stats['commits'] /
                                      repo_stats['weeks_old'])
    stats['commits'] += repo_stats['commits']
    repo_stats['additions_per_week'] = (repo_stats['code_additions'] /
                                        repo_stats['weeks_old'])
    repo_stats['deletions_per_week'] = (repo_stats['code_deletions'] /
                                        repo_stats['weeks_old'])
    stats['code_additions'] += repo_stats['code_additions']
    stats['code_deletions'] += repo_stats['code_deletions']

    # Get commit comment numbers, add to appropriate weeks member, calculate
    # comments per commit, and add to org stats.
    for comment in repo.iter_comments():
        repo_stats['commit_comments'] += 1
        comment_date = comment.to_json()['created_at'][:10]
        for week_start, repo_week_stat in repo_stats['weeks'].iteritems():
            next_week_start = next_week_iso(week_start)
            if week_start <= comment_date < next_week_start:
                org_week_stat = stats['weeks'][week_start]
                repo_week_stat['commit_comments'] += 1
                org_week_stat['commit_comments'] += 1
                if comment.user:
                    comment_author = unicode(comment.user)
                    if comment_author not in repo_week_stat['contributors']:
                        repo_week_stat['contributors'].append(comment_author)
                        repo_week_stat['contributor_count'] += 1
                    if comment_author not in org_week_stat['contributors']:
                        org_week_stat['contributors'].append(comment_author)
                        org_week_stat['contributor_count'] += 1
                break
    repo_stats['comments_per_commit'] = (repo_stats['commit_comments'] /
                                         float(repo_stats['commits']))
    stats['commit_comments'] += repo_stats['commit_comments']

    # Get issue, closed issue, and issue_comment numers, add to appropriate
    # weeks member, calculate issues per week, closed per week, and comments
    # per closed, and add to org stats.
    for issue in repo.iter_issues(state='all'):
        repo_stats['issues'] += 1
        issue_date = issue.to_json()['created_at'][:10]
        for week_start, repo_week_stat in repo_stats['weeks'].iteritems():
            next_week_start = next_week_iso(week_start)
            if week_start <= issue_date < next_week_start:
                org_week_stat = stats['weeks'][week_start]
                repo_week_stat['issues_opened'] += 1
                org_week_stat['issues_opened'] += 1
                if issue.user:
                    issue_author = unicode(issue.user.login)
                    if issue_author not in repo_week_stat['contributors']:
                        repo_week_stat['contributors'].append(issue_author)
                        repo_week_stat['contributor_count'] += 1
                    if issue_author not in org_week_stat['contributors']:
                        org_week_stat['contributors'].append(issue_author)
                        org_week_stat['contributor_count'] += 1
                break
        repo_stats['issue_comments'] += issue.comments
        for comment in issue.iter_comments():
            comment_date = comment.to_json()['created_at'][:10]
            for week_start, repo_week_stat in repo_stats['weeks'].iteritems():
                next_week_start = next_week_iso(week_start)
                if week_start <= comment_date < next_week_start:
                    org_week_stat = stats['weeks'][week_start]
                    repo_week_stat['issue_comments'] += 1
                    org_week_stat['issue_comments'] += 1
                    if comment.user:
                        comment_author = unicode(comment.user.login)
                        if comment_author not in repo_week_stat['contributors']:
                            repo_week_stat['contributors'].append(comment_author)
                            repo_week_stat['contributor_count'] += 1
                        if comment_author not in org_week_stat['contributors']:
                            org_week_stat['contributors'].append(comment_author)
                            org_week_stat['contributor_count'] += 1
                    break
        if issue.state == 'closed':
            repo_stats['closed_issues'] += 1
            issue_close_date = issue.to_json()['closed_at'][:10]
            for week_start, repo_week_stat in repo_stats['weeks'].iteritems():
                next_week_start = next_week_iso(week_start)
                if week_start <= issue_close_date < next_week_start:
                    org_week_stat = stats['weeks'][week_start]
                    repo_week_stat['issues_closed'] += 1
                    org_week_stat['issues_closed'] += 1
                    if issue.closed_by:
                        close_author = unicode(issue.closed_by.login)
                        if close_author not in repo_week_stat['contributors']:
                            repo_week_stat['contributors'].append(close_author)
                            repo_week_stat['contributor_count'] += 1
                        if close_author not in org_week_stat['contributors']:
                            org_week_stat['contributors'].append(close_author)
                            org_week_stat['contributor_count'] += 1
                    break
    repo_stats['issues_per_week'] = (repo_stats['issues'] /
                                     repo_stats['weeks_old'])
    repo_stats['closed_per_week'] = (repo_stats['closed_issues'] /
                                     repo_stats['weeks_old'])
    weekly_contributors = 0
    for week_stat in repo_stats['weeks'].itervalues():
        weekly_contributors += week_stat['contributor_count']
    repo_stats['contributors_per_week'] = (weekly_contributors /
                                           repo_stats['weeks_old'])
    if repo_stats['closed_issues']:
        repo_stats['comments_per_closed'] = (repo_stats['issue_comments'] /
                                             float(repo_stats['closed_issues']))
    stats['issues'] += repo_stats['issues']
    stats['closed_issues'] += repo_stats['closed_issues']
    stats['issue_comments'] += repo_stats['issue_comments']

# Calculate org ratios
stats['additions_per_week'] = (stats['code_additions'] / stats['weeks_old'])
stats['deletions_per_week'] = (stats['code_deletions'] / stats['weeks_old'])
stats['commits_per_week'] = (stats['commits'] / stats['weeks_old'])
stats['comments_per_commit'] = (stats['commit_comments'] /
                                float(stats['commits']))
stats['issues_per_week'] = (stats['issues'] / stats['weeks_old'])
stats['closed_per_week'] = (stats['closed_issues'] / stats['weeks_old'])
stats['comments_per_closed'] = (stats['issue_comments'] /
                               float(stats['closed_issues']))
stats['contributors_per_repo'] = (contributors / float(stats['repo_count']))
weekly_contributors = 0
for week_stat in stats['weeks'].itervalues():
    weekly_contributors += week_stat['contributor_count']
stats['contributors_per_week'] = (weekly_contributors / stats['weeks_old'])

json.dump(stats, open('./raw_data.json', 'w'), indent=4, separators=(',', ': '),
          sort_keys=True)

f = csv.writer(open('repo_summary_data.csv', 'wb+'))
header = ['repo', 'weeks_old', 'contributors', 'issues', 'issue_comments',
          'closed_issues', 'comments_per_closed', 'issues_per_week',
          'closed_per_week', 'commits', 'commit_comments',
          'comments_per_commit',  'commits_per_week', 'code_additions',
          'code_deletions', 'additions_per_week', 'deletions_per_week',
          'contributors_per_week']
f.writerow(header)
for repo, repo_stat in stats['repos'].iteritems():
    row = [repo]
    for key in header[1:]:
        row.append(repo_stat[key])
    f.writerow(row)
row = ['total']
for key in header[1:]:
    row.append(stats[key])
f.writerow(row)

f = csv.writer(open('org_weekly_data.csv', 'wb+'))
header = ['week_start', 'issues_opened', 'issue_comments', 'issues_closed',
          'commits', 'commit_comments', 'code_additions', 'code_deletions',
          'contributor_count']
f.writerow(header)
for week_start in sorted(stats['weeks']):
    week_stat = stats['weeks'][week_start]
    row = [week_start]
    for key in header[1:]:
        row.append(week_stat[key])
    f.writerow(row)
