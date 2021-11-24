import json
import re

def find_all(content, span):
    ret = []
    index = 0
    while True:
        index = content.find(span, index)
        if index == -1:
            break
        ret.append(index)
        index += len(span)
    return ret

def extend_span(span_i, span_j, data):
    inner_start = span_j["span_name"].find(span_i["span_name"])
    if inner_start != -1:
        extend_start = span_i["start_offset"] - inner_start
        extend_end = extend_start + len(span_j["span_name"])
        extend_name = data["content"][extend_start:extend_end]
        if extend_name == span_j["span_name"]:
            print("======= extend span ========")
            print("extend {} to {}".format(span_j["span_name"], extend_name))
            span_i["span_name"] = extend_name
            span_i["start_offset"] = extend_start
            span_i["end_offset"] = extend_end
    return

def extend_spans(data):
    spans = data["spans"]
    for i in range(len(spans)):
        for j in range(len(spans)):
            if i == j:
                continue
            span_i = spans[i]
            span_j = spans[j]
            if len(span_i["span_name"]) == len(span_j["span_name"]):
                continue
            elif len(span_i["span_name"]) < len(span_j["span_name"]):
                extend_span(span_i, span_j, data)
            else:
                extend_span(span_j, span_i, data)
    return

def reduce_spans(data):
    span_label_num = {}
    for span in data["spans"]:
        span_name = span["span_name"]
        label = span["label"]
        if span_name not in span_label_num:
            span_label_num[span_name] = {}
        span_label_num[span_name][label] = span_label_num[span_name].get(label, 0) + 1
    new_spans = []
    for span in data["spans"]:
        label_num = span_label_num[span["span_name"]]
        if len(label_num) == 1:
            new_spans.append(span)
            continue
        max_label_num = max(label_num.values())
        if label_num[span["label"]] == max_label_num:
            new_spans.append(span)
    if len(new_spans) != len(data["spans"]):
        print("======= reduce span ========")
        print(data["spans"])
        print(span_label_num)
        print(new_spans)
        data["spans"] = new_spans
    return

def add_span(data):
    cur_spans = data["spans"]
    if len(cur_spans) == 0:
        return
    span_set = set()
    for span in cur_spans:
        span_set.add((span["span_name"], span["label"]))
    new_spans = []
    content = data["content"]
    for span, label in span_set:
        all_place = find_all(content, span)
        for start_offset in all_place:
            end_offset = start_offset + len(span)
            new_spans.append(
                {
                    "span_name": span,
                    "label": label,
                    "start_offset": start_offset,
                    "end_offset": end_offset,
                }
            )
    if len(new_spans) != len(cur_spans):
        print("======= add span ========")
        print(cur_spans)
        print("-------------------------")
        print(new_spans)
    data["spans"] = new_spans
    return

def convert_label(data):
    doc_name_to_label = {
        "pochan.shuffle500.txt": "破产事件主体",
        "dongjiangaochengyuanyichang.shuffle500.txt": "董监高成员异常事件主体",
        "tingchanjianchan.shuffle5000.txt": "停产减产事件主体",
        "jianchi.shuffle500.txt": "减持事件主体",
        "pingjiehua.shuffle5000.txt": "评级恶化事件主体",
        "zichanyichang.shuffle5000.txt": "资产异常事件主体",
        "caiwuzaojia.shuffle5000.txt": "财务造假事件主体",
        "weiyueshixin.shuffle500.txt": "违约失信事件主体",
        "kuisun.shuffle500.txt": "亏损事件主体",
    }
    doc_name = data["doc_name"]
    if doc_name not in doc_name_to_label:
        return
    new_label = doc_name_to_label[doc_name]
    for span in data["spans"]:
        if span["label"] != new_label:
            print("============convert label===================")
            print(data["content"])
            print(span["span_name"], span["label"], new_label)
            span["label"] = new_label
    return
 

def add_span_all(input, output):
    with open(input) as f:
        datas = json.load(f)
    for data in datas["result"]:
        if len(data["spans"]) == 0:
            continue
        extend_spans(data)
        # reduce_spans(data)
        convert_label(data)
        # add_span(data)
    with open(output, "w") as f:
        json.dump(datas, f, ensure_ascii=False)
    return
    
def statis_doc_name(fp):
    with open(fp) as f:
        datas = json.load(f)
    doc_names = {}
    doc_names_num = {}
    for data in datas["result"]:
        doc_name= data["doc_name"]
        doc_names_num[doc_name] = doc_names_num.get(doc_name, 0) + 1
        doc_names[doc_name] = doc_names.get(doc_name, {})
        for span in data["spans"]:
            label = span["label"]
            doc_names[doc_name][label] = doc_names[doc_name].get(label, 0) + 1
    for k, v in doc_names.items():
        print(k, v, doc_names_num[k])
    return

  
if __name__ == "__main__":
#     statis_doc_name("/home/aipf/work/建行杯数据集/舆情预警/TestA/testA.json")
#     statis_doc_name("result/testA_result3.json")

    add_span_all("result/testA_result3.json", "result/testA_result4.json")
        
        