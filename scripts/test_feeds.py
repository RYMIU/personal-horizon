"""Phase 2 source discovery: fetch-test candidate feeds like Horizon's RSS scraper does."""
import concurrent.futures as cf
import json
import sys
from datetime import datetime, timezone

import feedparser
import httpx

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

CANDIDATES = [
    # --- China Tier A: official ---
    ("gov-zhengce-rsshub", "https://rsshub.app/gov/zhengce/zuixin", "CN", "china-news", "RSSHub"),
    ("gov-xinwen-rsshub", "https://rsshub.app/gov/xinwen/yaowen", "CN", "china-news", "RSSHub"),
    ("moe-rsshub", "https://rsshub.app/gov/moe/policy_anounce", "CN", "china-news", "RSSHub"),
    ("most-rsshub", "https://rsshub.app/gov/most/tzgg", "CN", "china-tech", "RSSHub"),
    ("stats-rsshub", "https://rsshub.app/gov/stats/sj/zxfb", "CN", "china-economy", "RSSHub"),
    ("pbc-rsshub", "https://rsshub.app/gov/pbc/goutongjiaoliu", "CN", "china-economy", "RSSHub"),
    ("nsfc-rsshub", "https://rsshub.app/gov/nsfc/tzgg", "CN", "china-news", "RSSHub"),
    ("cas-rsshub", "https://rsshub.app/cas/kyjz", "CN", "research-general", "RSSHub"),
    ("xinhua-rsshub", "https://rsshub.app/news/yaowen", "CN", "china-news", "RSSHub"),
    ("people-rss", "http://www.people.com.cn/rss/politics.xml", "CN", "china-news", "official-rss"),
    # --- China Tier B: professional media ---
    ("caixin-eco", "https://economy.caixin.com/feed/", "CN", "china-economy", "official-rss"),
    ("caixin-rsshub", "https://rsshub.app/caixin/latest", "CN", "china-news", "RSSHub"),
    ("yicai-rsshub", "https://rsshub.app/yicai/brief", "CN", "china-economy", "RSSHub"),
    ("jiemian-rsshub", "https://rsshub.app/jiemian/list/4", "CN", "china-news", "RSSHub"),
    ("36kr-feed", "https://36kr.com/feed", "CN", "china-tech", "official-rss"),
    ("jiqizhixin", "https://www.jiqizhixin.com/rss", "CN", "china-tech", "official-rss"),
    ("qbitai", "https://www.qbitai.com/feed", "CN", "china-tech", "official-rss"),
    ("infoq-cn", "https://www.infoq.cn/feed", "CN", "china-tech", "official-rss"),
    # --- International ---
    ("bbc-world", "https://feeds.bbci.co.uk/news/world/rss.xml", "INTL", "world-news", "official-rss"),
    ("guardian-world", "https://www.theguardian.com/world/rss", "INTL", "world-news", "official-rss"),
    ("nyt-world", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "INTL", "world-news", "official-rss"),
    ("cbc-top", "https://www.cbc.ca/webfeed/rss/rss-topstories", "INTL", "world-news", "official-rss"),
    ("cbc-world", "https://www.cbc.ca/webfeed/rss/rss-world", "INTL", "world-news", "official-rss"),
    ("ap-rsshub", "https://rsshub.app/apnews/topics/ap-top-news", "INTL", "world-news", "RSSHub"),
    # --- AI / Tech ---
    ("openai-news", "https://openai.com/news/rss.xml", "AI", "ai-tech", "official-rss"),
    ("anthropic-news", "https://www.anthropic.com/news/rss", "AI", "ai-tech", "official-rss"),
    ("deepmind-blog", "https://deepmind.google/blog/rss.xml", "AI", "ai-tech", "official-rss"),
    ("google-ai-blog", "https://blog.google/technology/ai/rss/", "AI", "ai-tech", "official-rss"),
    ("nvidia-blog", "https://blogs.nvidia.com/feed/", "AI", "ai-tech", "official-rss"),
    ("microsoft-ai-blog", "https://blogs.microsoft.com/ai/feed/", "AI", "ai-tech", "official-rss"),
    ("huggingface-blog", "https://huggingface.co/blog/feed.xml", "AI", "ai-tech", "official-rss"),
    ("simonwillison", "https://simonwillison.net/atom/everything/", "AI", "ai-tech", "official-rss"),
    ("mittr-ai", "https://www.technologyreview.com/feed/", "AI", "ai-tech", "official-rss"),
    ("techcrunch-ai", "https://techcrunch.com/category/artificial-intelligence/feed/", "AI", "ai-tech", "official-rss"),
    ("theverge-ai", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "AI", "ai-tech", "official-rss"),
    ("ars-ai", "https://arstechnica.com/ai/feed/", "AI", "ai-tech", "official-rss"),
    ("vllm-blog", "https://vllm.ai/blog/rss.xml", "AI", "ai-tech", "official-rss"),
    # --- Research ---
    ("nature-main", "https://www.nature.com/nature.rss", "RES", "research-general", "official-rss"),
    ("nature-comms", "https://www.nature.com/ncomms.rss", "RES", "research-general", "official-rss"),
    ("science-news", "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science", "RES", "research-general", "official-rss"),
    ("pnas", "https://www.pnas.org/action/showFeed?type=etoc&feed=rss&jc=pnas", "RES", "research-general", "official-rss"),
    ("arxiv-qbio-PE", "https://arxiv.org/rss/q-bio.PE", "RES", "research-personal", "official-rss"),
    ("arxiv-stat-ML", "https://arxiv.org/rss/stat.ML", "RES", "research-personal", "official-rss"),
    ("arxiv-math-OC", "https://arxiv.org/rss/math.OC", "RES", "research-personal", "official-rss"),
    ("arxiv-cs-LG", "https://arxiv.org/rss/cs.LG", "RES", "research-general", "official-rss"),
    ("biorxiv", "https://connect.biorxiv.org/biorxiv_xml.php?subject=all", "RES", "research-general", "official-rss"),
    ("medrxiv", "https://connect.medrxiv.org/medrxiv_xml.php?subject=all", "RES", "research-general", "official-rss"),
    ("siam-jmb-rsshub", "https://rsshub.app/springer/journal/285", "RES", "research-personal", "RSSHub"),
    ("mathbiosci-rsshub", "https://rsshub.app/elsevier/journal/0025-5564", "RES", "research-personal", "RSSHub"),
    ("or-journal-rsshub", "https://rsshub.app/informs/journal/opre", "RES", "research-personal", "RSSHub"),
    ("siam-news", "https://sinews.siam.org/rss", "RES", "research-general", "official-rss"),
    # --- Academic opportunity ---
    ("nsf-funding", "https://www.nsf.gov/funding/rss/rss_funding.xml", "ACA", "academic-opportunity", "official-rss"),
    ("nih-guide", "https://grants.nih.gov/funding/searchguide/rss/rss.xml", "ACA", "academic-opportunity", "official-rss"),
    ("canada-nserc", "https://www.canada.ca/en/natural-sciences-engineering-research-council/news.atom", "ACA", "academic-opportunity", "official-atom"),
    ("canada-cihr", "https://www.canada.ca/en/institutes-health-research/news.atom", "ACA", "academic-opportunity", "official-atom"),
    ("wellcome-rsshub", "https://rsshub.app/wellcome/news", "ACA", "academic-opportunity", "RSSHub"),
    ("simons", "https://www.simonsfoundation.org/feed/", "ACA", "academic-opportunity", "official-rss"),
    ("mitacs", "https://www.mitacs.ca/feed/", "ACA", "academic-opportunity", "official-rss"),
    ("ubc-grad", "https://www.grad.ubc.ca/feed", "ACA", "academic-opportunity", "official-rss"),
]

TIMEOUT = 20.0


def test_one(c):
    name, url, region, cat, method = c
    rec = {"name": name, "url": url, "region": region, "category": cat, "method": method}
    try:
        with httpx.Client(follow_redirects=True, timeout=TIMEOUT,
                          headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"}) as cli:
            r = cli.get(url)
        rec["http_status"] = r.status_code
        if r.status_code != 200:
            rec["status"] = "blocked"
            rec["error"] = f"HTTP {r.status_code}"
            return rec
        feed = feedparser.parse(r.content)
        if feed.bozo and not feed.entries:
            rec["status"] = "unstable"
            rec["error"] = f"parse: {str(feed.bozo_exception)[:120]}"
            return rec
        rec["entries"] = len(feed.entries)
        latest = None
        for e in feed.entries[:5]:
            for k in ("published_parsed", "updated_parsed"):
                t = e.get(k)
                if t:
                    dt = datetime(*t[:6], tzinfo=timezone.utc)
                    if latest is None or dt > latest:
                        latest = dt
        rec["latest_entry"] = latest.isoformat() if latest else None
        rec["feed_title"] = (feed.feed.get("title") or "")[:80]
        rec["status"] = "working" if feed.entries else "unstable"
        if not feed.entries:
            rec["error"] = "no entries"
    except Exception as ex:
        rec["status"] = "blocked"
        rec["error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
    return rec


def main():
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(test_one, CANDIDATES))
    for rec in results:
        print(json.dumps(rec, ensure_ascii=False))


if __name__ == "__main__":
    main()
