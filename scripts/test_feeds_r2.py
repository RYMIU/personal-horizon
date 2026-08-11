import concurrent.futures as cf, json
import feedparser, httpx
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CANDIDATES = [
    ("anthropic-rss", "https://www.anthropic.com/rss.xml", "AI"),
    ("meta-ai", "https://ai.meta.com/blog/rss/", "AI"),
    ("microsoft-blog", "https://blogs.microsoft.com/feed/", "AI"),
    ("nsf-funding2", "https://www.nsf.gov/funding/rss/funding.xml", "ACA"),
    ("nsf-news", "https://www.nsf.gov/news/newsroom.rss", "ACA"),
    ("nih-notices", "https://grants.nih.gov/guide/rss/notices.xml", "ACA"),
    ("nih-news", "https://grants.nih.gov/rss/news.xml", "ACA"),
    ("wellcome-news", "https://wellcome.org/rss/news", "ACA"),
    ("ubc-grad2", "https://www.grad.ubc.ca/rss.xml", "ACA"),
    ("canada-nserc2", "https://www.canada.ca/en/natural-sciences-engineering-research-council/news.atom?wbdisable=true", "ACA"),
    ("huxiu", "https://www.huxiu.com/rss/0.xml", "CN-TECH"),
    ("tmtpost", "https://www.tmtpost.com/rss.xml", "CN-TECH"),
    ("solidot", "https://www.solidot.org/index.rss", "CN-TECH"),
    ("cnbeta", "https://www.cnbeta.com.tw/backend.php", "CN-TECH"),
    ("36kr-newsflash", "https://36kr.com/newsflashes/rss", "CN-TECH"),
    ("thepaper-rsshub-pseudoyu", "https://rsshub.pseudoyu.com/thepaper/featured", "CN"),
    ("gov-pseudoyu", "https://rsshub.pseudoyu.com/gov/zhengce/zuixin", "CN"),
    ("gov-woodland", "https://rsshub.woodland.cafe/gov/zhengce/zuixin", "CN"),
    ("xinhua-pseudoyu", "https://rsshub.pseudoyu.com/news/yaowen", "CN"),
    ("moe-pseudoyu", "https://rsshub.pseudoyu.com/gov/moe/policy_anounce", "CN"),
    ("nsfc-pseudoyu", "https://rsshub.pseudoyu.com/gov/nsfc/tzgg", "CN"),
    ("stats-pseudoyu", "https://rsshub.pseudoyu.com/gov/stats/sj/zxfb", "CN-ECO"),
    ("pbc-pseudoyu", "https://rsshub.pseudoyu.com/gov/pbc/goutongjiaoliu", "CN-ECO"),
    ("caixin-pseudoyu", "https://rsshub.pseudoyu.com/caixin/latest", "CN"),
    ("yicai-pseudoyu", "https://rsshub.pseudoyu.com/yicai/brief", "CN-ECO"),
    ("jiemian-pseudoyu", "https://rsshub.pseudoyu.com/jiemian/list/4", "CN"),
    ("jiqizhixin-pseudoyu", "https://rsshub.pseudoyu.com/jiqizhixin/latest", "CN-TECH"),
    ("gnews-cn-gov", "https://news.google.com/rss/search?q=%E5%9B%BD%E5%8A%A1%E9%99%A2%20OR%20%E6%95%99%E8%82%B2%E9%83%A8%20OR%20%E7%A7%91%E6%8A%80%E9%83%A8%20when:2d&hl=zh-CN&gl=CN&ceid=CN:zh", "CN"),
    ("gnews-cn-ai", "https://news.google.com/rss/search?q=%E5%A4%A7%E6%A8%A1%E5%9E%8B%20OR%20%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%20when:2d&hl=zh-CN&gl=CN&ceid=CN:zh", "CN-TECH"),
]
def test_one(c):
    name, url, tag = c
    rec = {"name": name, "url": url, "tag": tag}
    try:
        with httpx.Client(follow_redirects=True, timeout=20.0, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"}) as cli:
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
