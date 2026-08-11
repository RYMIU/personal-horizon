import concurrent.futures as cf, json
import feedparser, httpx
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CANDIDATES = [
    ("nih-fundingopps", "https://grants.nih.gov/grants/guide/newsfeed/fundingopps.xml", "ACA"),
    ("nsf-rss-funding", "https://www.nsf.gov/rss/rss_funding.xml", "ACA"),
    ("nsf-funding-rss2", "https://www.nsf.gov/funding/rss/index.jsp", "ACA"),
    ("canada-news-atom", "https://www.canada.ca/en/news/advanced-news-search/news-results.atom?typ=newsreleases", "ACA"),
    ("wellcome-rss", "https://wellcome.org/rss.xml", "ACA"),
    ("ubc-grad-feed", "https://grad.ubc.ca/feed", "ACA"),
    ("ubc-gps", "https://www.gps.ubc.ca/feed", "ACA"),
    ("siam-smjmap", "https://epubs.siam.org/action/showFeed?type=etoc&feed=rss&jc=smjmap", "RES-OR"),
    ("informs-opre", "https://pubsonline.informs.org/action/showFeed?type=etoc&feed=rss&jc=opre", "RES-OR"),
    ("informs-ijoc", "https://pubsonline.informs.org/action/showFeed?type=etoc&feed=rss&jc=ijoc", "RES-OR"),
    ("elsevier-mbs", "https://rss.sciencedirect.com/publication/science/00255564", "RES-MB"),
    ("springer-jmb", "https://link.springer.com/search.rss?facet-content-type=%22Article%22&facet-journal-id=285&channel-language=en", "RES-MB"),
    ("plos-compbiol", "https://journals.plos.org/ploscompbiol/feed", "RES"),
    ("cell-current", "https://www.cell.com/cell/current.rss", "RES"),
    ("elife", "https://elifesciences.org/rss/recent.xml", "RES"),
    ("nat-mach-intell", "https://www.nature.com/natmachintell.rss", "RES-AI"),
    ("nat-comput-sci", "https://www.nature.com/natcomputsci.rss", "RES-AI"),
    ("chinanews", "https://www.chinanews.com.cn/rss/scroll-news.xml", "CN"),
    ("gnews-ca-policy", "https://news.google.com/rss/search?q=NSERC%20OR%20Mitacs%20OR%20CIHR%20funding%20when:14d&hl=en-CA&gl=CA&ceid=CA:en", "ACA"),
    ("gnews-phd", "https://news.google.com/rss/search?q=%22PhD%20position%22%20OR%20%22PhD%20funding%22%20mathematical%20biology%20OR%20epidemic%20when:14d&hl=en&gl=US&ceid=US:en", "ACA"),
]
def test_one(c):
    name, url, tag = c
    rec = {"name": name, "url": url, "tag": tag}
    try:
        with httpx.Client(follow_redirects=True, timeout=25.0, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"}) as cli:
            r = cli.get(url)
        rec["http_status"] = r.status_code
        if r.status_code != 200:
            rec["status"] = "blocked"; rec["error"] = f"HTTP {r.status_code}"; return rec
        feed = feedparser.parse(r.content)
        rec["entries"] = len(feed.entries)
        if feed.bozo and not feed.entries:
            rec["status"] = "unstable"; rec["error"] = f"parse: {str(feed.bozo_exception)[:100]}"; return rec
        rec["status"] = "working" if feed.entries else "unstable"
        rec["feed_title"] = (feed.feed.get("title") or "")[:60]
        if not feed.entries: rec["error"] = "no entries"
    except Exception as ex:
        rec["status"] = "blocked"; rec["error"] = f"{type(ex).__name__}: {str(ex)[:100]}"
    return rec
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for rec in ex.map(test_one, CANDIDATES):
        print(json.dumps(rec, ensure_ascii=False))
