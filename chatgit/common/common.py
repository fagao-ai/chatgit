from pathlib import Path


PROJECT_PATH = Path(__file__).absolute().parent.parent.parent

CRAWL_DATA  = PROJECT_PATH / "crawl_data"

if not CRAWL_DATA.exists():
    CRAWL_DATA.mkdir()