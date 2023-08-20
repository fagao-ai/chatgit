import jsonlines


from chatgit.common.common import CRAWL_DATA


with jsonlines.open(CRAWL_DATA / "crawl-success.jsonlines") as reader:
    for json_data in reader:
        # json_data 是一个字典，包含当前行中的 JSON 数据
        print(json_data)