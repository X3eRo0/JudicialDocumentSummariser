"""
    This file is part of Judicial Document Summariser.
    Judicial Document Summariser is free software: you can redistribute it and/or modify it under the terms of the 
    GNU General Public License as published by the Free Software Foundation, either version 3 
    of the License, or (at your option) any later version.
    Judicial Document Summariser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
    See the GNU General Public License for more details.
    You should have received a copy of the GNU General Public License along with AFL-Cast. 
    If not, see <https://www.gnu.org/licenses/>. 
"""
import random
import tkinter as tk
from tkinter import StringVar, ttk
from tkinter import filedialog
from functools import partial
import tkpdf
import pdftotext
# from Crawler import *
from sumy.evaluation.rouge import *
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.evaluation.coselection import *
from sumy.utils import get_stop_words
from Codes.klsum import GetKLSummary
from Codes.lex_rank import GetLexRankSummary
from Codes.lsa import GetLsaSummary
from Codes.luhn import GetLuhnSummary
from Codes.term_frequency import GetTermFrequencySummary
from Codes.similarity import GetSimilarity
from Codes.text_rank import GetTextRankSummary

# constants
BORDERWIDTH = 5
RELEIFSTYLE = tk.GROOVE
WIDTH = 1020
HEIGHT = 600


def getPDFText2(filename):
    with open(filename, "rb") as file:
        pdf = pdftotext.PDF(file)
        file.close()
    data = ""
    for page in pdf:
        data += page
    file.close()
    return data


ALGORITHMS = {
    "TextRank": GetTextRankSummary,
    "LexRank": GetLexRankSummary,
    "LSA": GetLsaSummary,
    "Luhn": GetLuhnSummary,
    "KLSum": GetKLSummary,
    "TermFrequency": GetTermFrequencySummary,
}

class Application:
    """
    Kanoon Software:
        Application class to handle elements in the GUI.
        +----------+----------+----------+
        |          |          |          |
        |   PDF    |  Summary | Control  |
        |  Viewer  |  Editor  |  Panel   |
        |          |          |          |
        |          |          |          |
        +----------+----------+----------+
    """

    def __init__(self, title):
        self.pdffile = None  # pdf to open
        self.root = tk.Tk()
        self.root.title(title)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        # self.resize(WIDTH, HEIGHT)
        self.menu_bar()
        self.summary_panel()
        self.control_panel()

    def menu_bar(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.filemenu = tk.Menu(self.menu)
        self.editmenu = tk.Menu(self.menu)
        self.helpmenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.menu.add_cascade(label="Edit", menu=self.editmenu)
        self.menu.add_cascade(label="Help", menu=self.helpmenu)
        self.filemenu.add_command(label="Open", command=self.load_pdf)
        self.filemenu.add_command(label="Exit", command=exit)
        self.helpmenu.add_command(label="About", command=self.help)
        self.editmenu.add_command(label="Undu")
        self.editmenu.add_command(label="Redu")

    def summary_panel(self):
        self.left = tk.Frame(self.root, relief=RELEIFSTYLE, borderwidth=BORDERWIDTH)
        self.middle = tk.Frame(self.root, relief=RELEIFSTYLE, borderwidth=BORDERWIDTH)
        label = tk.Label(master=self.middle, text="Your Summary")
        self.summarybox = tk.Text(master=self.middle, wrap=tk.WORD)
        horizontal_scroll = ttk.Scrollbar(
            self.middle, orient="horizontal", command=self.summarybox.xview
        )
        vertical_scroll = ttk.Scrollbar(
            self.middle, orient="vertical", command=self.summarybox.yview
        )
        self.summarybox.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )
        vertical_scroll.pack(side=tk.RIGHT, fill=tk.BOTH)
        horizontal_scroll.pack(side=tk.BOTTOM, fill=tk.BOTH)
        label.pack()
        self.summarybox.pack(expand=True, fill=tk.BOTH)
        self.left.grid(row=0, column=0, sticky="nsew")
        self.middle.grid(row=0, column=1, sticky="nsew")

    def open_document(self):
        w = self.root.winfo_width()
        if w == WIDTH:
            self.resize(WIDTH + 600, HEIGHT)
        else:
            self.clear_frame(self.left)
            self.left.destroy()
            self.left = tk.Frame(self.root, relief=RELEIFSTYLE, borderwidth=BORDERWIDTH)
            self.left.grid(row=0, column=0, sticky="nsew")

        filename = self.load_pdf()
        if filename is None:
            return
        self.pdffile = filename.name
        pdf = tkpdf.PdfView(master=self.left, file=filename)
        pdf.pack(expand=True, fill=tk.BOTH)

    def close_document(self):
        self.clear_frame(self.left)
        self.left.destroy()
        self.left = tk.Frame(self.root, relief=RELEIFSTYLE, borderwidth=BORDERWIDTH)
        self.left.grid(row=0, column=0, sticky="nsew")
        self.resize(WIDTH, HEIGHT)

    def control_panel(self):
        self.right = tk.LabelFrame(self.root, text="Control Panel", relief=RELEIFSTYLE, borderwidth=BORDERWIDTH)
        openpdfbutton = tk.Button(
            master=self.right, text="Open PDF", command=self.open_document
        )
        closepdfbutton = tk.Button(
            master=self.right, text="Close", command=self.close_document
        )
        options = list(ALGORITHMS.keys())
        self.clicked = tk.StringVar()
        self.clicked.set(options[0])
        algos = tk.OptionMenu(self.right, self.clicked, *options)
        nsentences = tk.Entry(self.right, width=2)
        gensummary = tk.Button(
            master=self.right, text="Get Summary", command=partial(self.generate_summary, nsentences)
        )
        tk.Label(master=self.right, text="\nInput Document:  ").grid(row=1, column=0, sticky="ew")
        openpdfbutton.grid(row=2, column=0, sticky="ew")
        closepdfbutton.grid(row=2, column=1, sticky="ew")
        tk.Label(master=self.right, text="\nSummary Generation: ").grid(row=3, column=0, sticky="ew")
        algos.grid(row=4, column=0, sticky="ew")
        tk.Label(master=self.right, text="Select Algorithm").grid(row=4, column=1, sticky="ew")
        nsentences.grid(row=5, column=0, sticky="ew")
        tk.Label(master=self.right, text="# of sentences in summary").grid(row=5, column=1, sticky="ew")
        gensummary.grid(row=6, column=0, sticky="ew", columnspan=3)
        tk.Label(master=self.right, text="\nCompare Documents: ").grid(row=7, column=0, sticky="ew")
        pdf1text = tk.Label(master=self.right, text="Select Document")
        pdf1text.grid(row=8, column=1, sticky="ew")
        pdf2text = tk.Label(master=self.right, text="Select Document")
        pdf2text.grid(row=9, column=1, sticky="ew")
        self.pdf1 = None
        self.pdf2 = None
        score = tk.Label(master=self.right, text="")
        pdf1 = tk.Button(master=self.right, text="Choose Document 1", command=partial(self.open_pdf_and_update, pdf1text, 1))
        pdf2 = tk.Button(master=self.right, text="Choose Document 2", command=partial(self.open_pdf_and_update, pdf2text, 2))
        pdf3 = tk.Button(master=self.right, text="Get Similarity Score", command=partial(self.get_comparison, score))
        pdf1.grid(row=8, column=0)
        pdf2.grid(row=9, column=0)
        pdf3.grid(row=10, column=0, columnspan=10)
        score.grid(row=11, column=0, columnspan=10)
        self.right.grid(row=0, column=2, sticky="nsew")

    def open_pdf_and_update(self, pdflabel, pdffile):
        filename = self.load_pdf()
        pdflabel.config(text=filename.name.split("/")[-1])
        if pdffile == 1:
            self.pdf1 = filename
        else:
            self.pdf2 = filename

    def get_comparison(self, score):
        if self.pdf1 is None or self.pdf2 is None:
            return

        score.config(text="%f%% similar" % (100.0 * GetSimilarity(self.pdf1.name, self.pdf2.name)))


    def generate_summary(self, nsentences):
        if self.pdffile is None or self.clicked is None:
            return
        pdffile = self.pdffile
        algo = self.clicked.get()
        function = ALGORITHMS[algo]
        nsentences = nsentences.get()
        try:
            nsentences = int(nsentences)
        except:
            nsentences = 25

        text = function(pdffile, nsentences)
        self.summarybox.delete("1.0", "end")
        for i in range(len(text)):
            self.summarybox.insert("%f" % (i+1), text[i]+"\n")
            print(i+1, text[i])

    def help(self):
        pass

    def resize(self, w, h):
        self.root.geometry("%dx%d+400+100" % (w, h))

    def clear_frame(self, frame: tk.Frame):
        for child in frame.winfo_children():
            child.destroy()

    def load_pdf(self):
        filename = filedialog.askopenfile()
        return filename

    def mainloop(self):
        self.root.mainloop()


app = Application("Judicial Document Summariser")
app.mainloop()
