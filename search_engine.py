import os
from pdftabextract.common import read_xml, parse_pages
# from bs4 import BeautifulSoup
import textract
from PyPDF2 import PdfFileReader

path = input("Enter your PDF file path: ")
if not os.path.exists('single_pdfs'):
    print('Converting PDF to a single page...')
    os.makedirs('single_pdfs')
    os.system("pdftk {} burst output /home/lemma/single_pdfs/pg-%01d.pdf".format(path))
inputpdf = PdfFileReader(open(path, "rb"))
texts = {}
key = []
for i in range(1, inputpdf.numPages + 1):
    try:
        text = textract.process("/home/lemma/single_pdfs/pg-{}.pdf".format(i))
        s = ""
        for x in text.split():
            s += x.decode('utf-8') + " "
        if s != "":
            key.append(i)
            texts[i] = s
    except:
        print('skipping at page', i)
        continue
    if i % 100 == 0:
        print(i)
#############BeautifulSoup technique#############
#################################################
# with open(path_XML+'output.xml', 'r') as tei:
#    soup = BeautifulSoup(tei, 'lxml')
#    s=repr(soup.text)#to show \n
#################################################
#############pdftabextract technique#############
#################################################
# xmltree, xmlroot = read_xml(os.path.join(path_XML, 'output.xml'))
# for p in xmlroot.findall('page'):
#    for t in p.findall('text'):
#        print(' '.join(t.itertext()))
# pages = parse_pages(xmlroot)
# texts=[]
# for i in range(1,len(pages)):
#    p = pages[i]
#    tex=[x['value'] for x in p['texts'] if x['height']==17 and x['value']!=" "]
#    if tex:
#        texts.append(''.join(tex))
#################################################
import math


class VectorCompare:
    def magnitude(self, concordance):
        if type(concordance) != dict:
            raise ValueError('Supplied Argument should be of type dict')
        total = 0
        for word, count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    def relation(self, concordance1, concordance2):
        if type(concordance1) != dict:
            raise ValueError('Supplied Argument 1 should be of type dict')
        if type(concordance2) != dict:
            raise ValueError('Supplied Argument 2 should be of type dict')
        relevance = 0
        topvalue = 0
        for word, count in concordance1.items():
            if word in concordance2:
                topvalue += count * concordance2[word]

        if (self.magnitude(concordance1) * self.magnitude(concordance2)) != 0:
            return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))
        else:
            return 0

    def concordance(self, document):
        con = {}
        for word in document.split(' '):
            if word in con:
                con[word] = con[word] + 1
            else:
                con[word] = 1
        return con


v = VectorCompare()
index = {}
for i in key:
    index[i] = v.concordance(texts[i].lower())
try:
    while True:
        searchterm = input('Enter query: ')
        matches = []

        for i in key:
            relation = v.relation(v.concordance(searchterm.lower()), index[i])
            if relation != 0:
                matches.append((relation, texts[i]))

        matches.sort(reverse=True)
        x = 1
        file = open("summary_{}.txt".format(searchterm), "w")
        for i in matches:
#            if i[0] < 0.10:
#                break
            if x==11:
                break
            file.write(i[1]+ '\n'+'\n')
            file.flush()
            print('DOCUMENT {}'.format(x),'||',i[1])
            print('************************')
            print('')
            x += 1
        print('-------------------END OF QUERY: {}. TO EXIT QUERY, PRESS CTRL+C-------------------'.format(searchterm))
        print('')
except KeyboardInterrupt:
    print('')
    print("DONE")
    pass
import shutil

shutil.rmtree('/home/lemma/single_pdfs')
