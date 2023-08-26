import jsonlines

from chatgit.common.common import CRAWL_DATA

with jsonlines.open(CRAWL_DATA / "crawl-success.jsonlines") as reader:
    for json_data in reader:
        print(json_data.keys())
        print(json_data["forks_count"])
        break
