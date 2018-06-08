import yaml, sys, os, glob
import re

import argparse

from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

print(sys.argv)

parser = argparse.ArgumentParser(description='Convert Moodle GIFT files to Coursera YAML.')
parser.add_argument('--splits', metavar='splits', type=int, nargs=1, default=1,
    help='how many questions to split into')

parser.add_argument('--match', metavar='match', default=None,
    help='a string which much be matched in the question text for the question to be converted')

parser.add_argument('files', metavar='files', nargs='+',
                     help='the files to convert')

args = parser.parse_args()

print(args)

num_splits = args.splits[0]
match = args.match
print(num_splits)
print(match)

file_names = args.files
#for f in args.files:
#    print(f)
#    print(glob.glob(f))
#    file_names + file_names + glob.glob(f)
print (file_names)

#sys.exit()

#file_name = sys.argv[2]
#num_splits = int(sys.argv[1])

#print(file_name)
#print(num_splits)

for file_name in file_names:
    print(file_name)

    file = open(file_name, 'r')
    gift_text = file.read()
    gift_text = gift_text.replace("\{", "%%open_curly%%")
    gift_text = gift_text.replace("\}", "%%close_curly%%")
    file.close()

    file_name, file_extension = os.path.splitext(file_name)
    print(file_name)
    print(file_extension)

    #print (gift_text)

    questionsrex = "::(.*)::([^{]*){([^}]*)}"
    #questionsrex = "::(.*)::\[(.*)\]([^{]*){([^}]*)}"
    answersrex = "\t([=~][^\t]*)"

    result = re.findall(questionsrex, gift_text)
    #print(len(result))
    #print(result[6][1])

    qs = []
    for res in result:
        qs.append({})

        #print (res[1])
        res = [r.replace("<br>", " ") for r in res]
        res = [r.replace("<p>", "\n") for r in res]
        res = [r.replace("</p>", "\n") for r in res]
        res = [r.replace("&nbsp;", "\n") for r in res]
        res = [strip_tags(r) for r in res]
        #print(res[1])
        res = [r.replace("%%open_curly%%", "{") for r in res]
        res = [r.replace("%%close_curly%%", "}") for r in res]
        res = [r.replace("\_", " ") for r in res]
        res = [r.replace("[moodle]", "") for r in res]
        res = [r.replace("[html]", "") for r in res]
        res = [r.replace("[", "\[") for r in res]
        res = [r.replace("]", "\]") for r in res]
        res = [r.replace("\\\\\\hline", "\\\\ \\hline") for r in res]
        res = [r.replace("\\\\", "\\") for r in res]
        def replBackslash(s):
            return s.group(0)[1:]
        #res = [re.sub("\\\\\w", replBackslash, r) for r in res]


        #print(res[2])
        qs[-1]["answers"] = re.findall(answersrex, res[2])
        #res = [r.strip() for r in res]

        #print(res[1])

        qs[-1]["name"] = res[0]
        qs[-1]["question"] = res[1]

    if match != None :
        qs = [q for q in qs if (q["name"].find(match) >=0)]

    if num_splits == "all":
        question_list = [[q] for q in qs]
    else:
        split_size = int(len(qs)/num_splits)
        question_list = [qs[i*split_size: (i+1)*split_size] for i in range(num_splits-1)]
        question_list.append(qs[(num_splits-1)*split_size:])
    #print(len(qs))
    #print ([len(q) for q in question_list])

    yqs = []
    for qs in question_list:
        yqs.append({})
        current_variations = []
        for q in qs :

            yq = {}
            #print(q["answers"])
            #if (q["answers"][0][1] == "%"):
            #    yq["typeName"] = "numeric"
            #else:
            yq["typeName"] = "multipleChoice"
            yq["shuffleOptions"] = True
            yq["prompt"] = q["question"].strip()#.replace("\\\\\\hline","\\\\ \\hline").replace("\\\\","\\")#.replace("YAYAYA", "\\")

            yq["options"] = []
            numCorrect = 0
            for answer in q["answers"]:
                a = {}
                answer = answer.strip()
                answertext = answer[1:].strip().split("#")
                a["answer"] = answertext[0].split("%")[-1]
                percentage = 0
                if(len(answertext[0].split("%")) > 1):
                   percentage = int(answertext[0].split("%")[-2])
                #print(percentage)
                if(len(answertext)>1):
                    a["feedback"] = answer[1:].split("#")[1]
                a["isCorrect"] = True if (answer[0] == "=" or percentage > 0) else False
                if a["isCorrect"] :
                    numCorrect += 1
                yq["options"].append(a)
            #print(numCorrect)
            if numCorrect == len(yq["options"]):
               yq["typeName"] = "text"
               yq["answers"] = yq["options"]
               yq["defaultFeedback"] = ""
               del yq["options"]
            if(numCorrect > 1 and yq["typeName"] == "multipleChoice"):
                yq["typeName"] = "checkbox"
            current_variations.append(yq)

        yqs[-1]["variations"] = current_variations
    #print (yaml.dump(yqs))

    outfile = open(file_name+"-"+str(num_splits)+".yaml", "w")
    yaml.dump(yqs, outfile)
    outfile.close()
