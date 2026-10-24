"""Fetches the numbers the profile charts show and writes them to ./data.

Needs GITHUB_TOKEN in the environment (the Actions token is enough). Package numbers come
from the public NuGet, npm and pub.dev APIs. Anything that fails keeps its previous value,
so a flaky API never blanks a chart.
"""
import json
import os
import urllib.request
from pathlib import Path

LOGIN = "BeratARPA"
DATA = Path(os.environ.get("PROFILE_ROOT", Path(__file__).parent)) / "data"
DATA.mkdir(exist_ok=True)


def get(url, headers=None, body=None):
    req = urllib.request.Request(url, data=body, headers={"User-Agent": "profile-charts", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def graphql(query):
    token = os.environ["GITHUB_TOKEN"]
    out = get("https://api.github.com/graphql", {"Authorization": f"bearer {token}", "Content-Type": "application/json"},
              json.dumps({"query": query}).encode())
    if "errors" in out:
        raise RuntimeError(out["errors"])
    return out


def save(name, value):
    (DATA / name).write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")


def load(name, default):
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def step(label, fn):
    try:
        fn()
        print("ok  ", label)
    except Exception as e:  # keep the old file, report and move on
        print("FAIL", label, e)


def contributions():
    save("contrib.json", graphql(
        f'{{ user(login:"{LOGIN}") {{ contributionsCollection {{ contributionCalendar {{ totalContributions '
        f'weeks {{ contributionDays {{ date contributionCount }} }} }} restrictedContributionsCount }} }} }}'))


def stars():
    total, cursor, per_repo = 0, None, {}
    while True:
        after = f', after:"{cursor}"' if cursor else ""
        page = graphql(f'{{ user(login:"{LOGIN}") {{ repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false{after}) '
                       f'{{ pageInfo {{ hasNextPage endCursor }} nodes {{ name stargazerCount }} }} }} }}')["data"]["user"]["repositories"]
        for n in page["nodes"]:
            total += n["stargazerCount"]
            per_repo[n["name"]] = n["stargazerCount"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    summary = load("summary.json", {})
    summary["stars"] = total
    summary["repo_stars"] = per_repo
    save("summary.json", summary)


def packages():
    pkgs = load("packages.json", {})

    def nuget(pid):
        hits = get(f"https://azuresearch-usnc.nuget.org/query?q=packageid:{pid}&prerelease=true")["data"]
        return next(h["totalDownloads"] for h in hits if h["id"].lower() == pid.lower())

    for key, fn in [("nuget_printhtml", lambda: nuget("PrintHTML.Core")),
                    ("nuget_are", lambda: nuget("ARE.Core")),
                    ("npm_are", lambda: get("https://api.npmjs.org/downloads/point/2020-01-01:2099-01-01/are-engine-core")["downloads"]),
                    ("pub_points", lambda: get("https://pub.dev/api/packages/are_engine_core/score")["grantedPoints"])]:
        try:
            pkgs[key] = fn()
        except Exception as e:
            print("FAIL", key, e)
    save("packages.json", pkgs)


step("contributions", contributions)
step("stars", stars)
step("packages", packages)
