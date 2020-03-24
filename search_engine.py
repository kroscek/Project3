import os
from pdftabextract.common import read_xml, parse_pages
# from bs4 import BeautifulSoup
import textract
from PyPDF2 import PdfFileReader
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
import io
import shutil


class GUI:
    def __init__(self, root):
        self.root = root
        
        self.ll=Label(self.root, text="1. PDF Upload:", font = ("Arial 12 bold"))
        self.ll.grid(row=0, column=0, padx=5, pady = 0, sticky="W")
        
        self.l=Text(self.root, height=1, width=60, padx=5, bg='white',
                                     borderwidth=4, highlightthickness=0,
                                     relief='ridge')
        self.l.grid(row=0,column=1,columnspan=2)
        self.button = Button(self.root, text='Upload', command=self.UploadAction)
        self.button.grid(row=0,column=3)
    
    
        self.lll=Label(self.root, text="2. PDF Processing:", font = ("Arial 12 bold"))
        self.lll.grid(row=1, column=0, padx=5, pady = 0, sticky="W")
        self.progress_var = DoubleVar()
        self.progress=Progressbar(root, variable=self.progress_var)
        self.progress.grid(row=1,column=3)
        self.button1=Button(self.root, text='Start', command=self.PDF_processing)
        self.button1.grid(row=1,column=1,padx=5, pady = 0, sticky="W")
        self.label = Label(self.root)
        self.label.grid(row=1,column=2)
        
        self.llll=Label(self.root, text="3. Input your Query:", font = ("Arial 12 bold"))
        self.llll.grid(row=2, column=0, padx=5, pady = 0, sticky="W")
        self.query=Text(self.root, height=1, width=60, padx=5, bg='white',
                                     borderwidth=4, highlightthickness=0,font = "Arial 12 bold",
                                     relief='ridge')
        self.query.grid(row=2,column=1,columnspan=2)
        self.button2=Button(self.root, text='Search', command=self.search_engine)
        self.button2.grid(row=2,column=3)
        self.result=Text(self.root, height=50, width=130, padx=5, bg='white',
                                     borderwidth=4, highlightthickness=0,
                                     relief='ridge')
        self.result.grid(row=3,column=0,columnspan=10)
        self.result.config(state=NORMAL)
        
    def search_engine(self,evt=None):
        self.result.delete("1.0",END)#clear previously texts before start a new query
        x=self.retrieve_query()
        self.calculate(x)
        
    def UploadAction(self,event=None):
        self.filename = filedialog.askopenfilename(title="Select PDF file",filetypes=(("Document files", "*.pdf"), ("All files", "*.*")))
        self.l.insert(END,self.filename)
        
    def retrieve_query(self):
        inputValue=self.query.get("1.0","end-1c")
        self.query.delete('1.0', END)# clear query after press button search
        print(inputValue)
        return inputValue
    
    def PDF_processing(self):
        self.label.config(text = "Converting PDF to a single page...")
        self.label.update_idletasks()
        if not os.path.exists('single_pdfs'):
            os.makedirs('single_pdfs')
            os.system("pdftk {} burst output /home/lemma/single_pdfs/pg-%01d.pdf".format(self.filename))
        inputpdf = PdfFileReader(open(self.filename, "rb"))
        self.texts = {}
        self.key = []
        self.label.config(text = "Converting a pdf page to text...")
        
        self.label.update_idletasks()
        self.progress.config(maximum=inputpdf.numPages)
        for i in range(1, inputpdf.numPages + 1):
            self.progress_var.set(i)
            try:
                text = textract.process("/home/lemma/single_pdfs/pg-{}.pdf".format(i))
                s = ""
                for x in text.split():
                    s += x.decode('utf-8') + " "
                if s != "":
                    self.key.append(i)
                    self.texts[i] = s
            except:
#                self.label.config(text = " skipping at page {}".format(i))
#                self.label.update_idletasks()      
                continue
            if i % 100 == 0:
                print(i)
            self.root.update_idletasks()
        self.label.config(text = "FINISH")
    
    def calculate(self,query):
        buffer = io.StringIO()
        v = VectorCompare()
        index = {}
        for i in self.key:
            index[i] = v.concordance(self.texts[i].lower())
        searchterm = query
        matches = []
        for i in self.key:
            relation = v.relation(v.concordance(searchterm.lower()), index[i])
            if relation != 0:
                matches.append((relation, self.texts[i]))

        matches.sort(reverse=True)
        x = 1
        file = open("summary_{}.txt".format(searchterm), "w")
        for i in matches:
#            if i[0] < 0.10:#RETURN TOP 10% DOCUMENTS so it can be more than 10 documents retrieved
#                break
            if x==11:#RETURN TOP 10 DOCUMENTS
                break
            file.write(i[1]+ '\n'+'\n')
            file.flush()
            print('DOCUMENT {}'.format(x),'||',i[1],file=buffer)
            print('************************',file=buffer)
            print('',file=buffer)
            
            x += 1
        print('-------------------END OF QUERY: {}-------------------'.format(
                searchterm),file=buffer)
        print('',file=buffer)
        output = buffer.getvalue()
        self.result.insert(END, output)
        
root = Tk()
GUI(root)
root.title('PDF Search Engine')
root.resizable(0, 0)
root.mainloop()
shutil.rmtree('/home/lemma/single_pdfs')
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


