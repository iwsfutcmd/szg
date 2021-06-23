import requests
from bs4 import BeautifulSoup
import regex as re
from glob import glob
import csv

def eguidedog_extract():
    urls = [f"https://www.eguidedog.net/chinese/three-character-classic{n}.php" for n in ["", "2", "3", "4", "5"]]

    lzh_Hant_sub = {
        "能溫席": "能温席", #34
        "此六谷": "此六穀", #75
        "雞犬豕": "鷄犬豕", #78
        "與絲竹": "絲與竹", #87
        "至玄曾": "至元曾", #94 (changed in Giles for taboo)
        "名句讀": "明句讀", #110
        "有彀梁": "有穀梁", #166
        "王綱墮": "王綱墜", #204
        "尚游說": "尙遊說", #206
        "五霸強": "五霸强", #209
        "始兼並": "始兼幷", #212
        "興高齊": "與高齊", #234
        "迨至隋": "逮至隋", #235
        "全在茲": "全在玆", #256
        "讀史書": "讀史者", #259
        "尚勤學": "尙勤學", #270
        "學不綴": "學不輟", #286
        "彼既成": "彼晚成", #303
        "衆稱異": "眾稱異", #304
        "宜立誌": "宜立志", #306
        "能詠詩": "能咏詩", #308
        "能詠吟": "能咏吟", #318
        "勉而緻": "勉而致", #330
        "雞司晨": "鷄司晨", #334
        "上緻君": "上致君", #343
        "金滿嬴": "金滿籯", #350

    }
    cmn_sub = {
        "yu3 si1 zhu2": "si1 yu3 zhu2", #87
        "you3 gou4 liang2": "you3 gu3 liang2", #166
        "xing4 gao1 qi2": "yu3 gao1 qi2", #234
        "du2 shi3 shu1": "du2 shi3 zhe3", #259
        "xue2 bu4 zhui5": "xue2 bu4 chuo4", #286
        "bi3 ji4 cheng2": "bi3 wan3 cheng2", #303
    }
    yue_sub = {
        "jyu5 si1 zuk1": "si1 jyu5 zuk1", #87
        "jau5 gau3 loeng4": "jau5 guk1 loeng4", #166
        "hing1 gou1 cai4": "jyu5 gou1 cai4", #234
        "wong4 gong1 zeio6": "wong4 gong1 zeoi6", #204
        "duk6 si2 syu1": "duk6 si2 ze2", #259
        "hok6 bat1 zeoi3": "hok6 bat1 zyui3", #286
        "bei2 gei3 sing4": "bei2 maan5 sing4", #303
        
    }

    cmn_lines = []
    yue_lines = []
    lzh_Hant_lines = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        for clause in soup.find_all(class_="pinyin"):
            clause_line = re.sub(r"(【.*】|,)", "", clause.text).strip()
            syllables = clause_line.split(" ")
            for i in range(len(syllables) // 3):
                line = " ".join(syllables[i*3:i*3+3])
                cmn_lines.append(cmn_sub.get(line, line))
        for clause in soup.find_all(class_="jyutping"):
            clause_line = re.sub(r"(【.*】|,)", "", clause.text).strip()
            if clause_line.endswith("leon"):
                clause_line = clause_line + "4"
            syllables = clause_line.split(" ")
            for i in range(len(syllables) // 3):
                line = " ".join(syllables[i*3:i*3+3])
                yue_lines.append(yue_sub.get(line, line))
        for clause in soup.find_all(class_="traditional"):
            clause_line = re.sub(r"【.*】", "", clause.text).strip()
            for line in re.findall(r"\p{Han}{3}", clause_line):
                lzh_Hant_lines.append(lzh_Hant_sub.get(line, line))

    with open("cmn_lines.csv", "w") as file:
        file.write("\n".join(cmn_lines))

    with open("yue_lines.csv", "w") as file:
        file.write("\n".join(yue_lines))

    with open("lzh_Hant_lines.csv", "w") as file:
        file.write("\n".join(lzh_Hant_lines))

def wikisource_soup_extract(soup):
    output = []
    for i, table in enumerate(soup("table")):
        entry = {}
        entry["number"] = table.tr.td.text.strip().strip(".")
        entry["zho"] = [td.text.strip() for td in table.tr("td")[1:4]]
        try:
            entry["meaning"] = table.tr("td")[5].text.strip()
        except IndexError:
            entry["meaning"] = ""
        entry["cmn"] = [td.text.strip() for td in table("tr")[1]("td")[1:4]]
        entry["eng"] = [td.text.strip() for td in table("tr")[2]("td")[1:4]]
        output.append(entry)
    return output

def wikisource_extract():
    filenames = sorted(glob("OPS/c*_San_Tzu_Ching_San_Tzu_Ching*.xhtml")) + sorted(glob("OPS/c*_San_Tzu_Ching_Appendix_*.xhtml"))
    output = []
    for filename in filenames:
        soup = BeautifulSoup(open(filename), "lxml")
        output.extend(wikisource_soup_extract(soup))
    with open("wikisource.csv", "w") as file:
        writer = csv.writer(file, dialect="excel-tab")
        for entry in output:
            line = [entry["number"], "".join(entry["zho"]), " ".join(entry["cmn"]).lower(), " | ".join(entry["eng"]).lower(), entry["meaning"]]
            writer.writerow(line)
    return output