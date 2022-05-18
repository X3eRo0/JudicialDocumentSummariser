"""
    This file is part of KanoonSoftware.
    KanoonSoftware is free software: you can redistribute it and/or modify it under the terms of the 
    GNU General Public License as published by the Free Software Foundation, either version 3 
    of the License, or (at your option) any later version.
    KanoonSoftware is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
    See the GNU General Public License for more details.
    You should have received a copy of the GNU General Public License along with AFL-Cast. 
    If not, see <https://www.gnu.org/licenses/>. 
"""

import tkinter as tk
from tkinter import StringVar, ttk
from tkinter import filedialog
from functools import partial
import tkpdf
import pdftotext
from Crawler import *
from sumy.evaluation.rouge import *
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.kl import KLSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.evaluation.coselection import *
from sumy.utils import get_stop_words

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


def GetTextRankSummary(filename, nsentences):
    data = getPDFText2(filename)
    parser = PlaintextParser.from_string(data, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = TextRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")
    text = [a._text for a in summarizer(parser.document, nsentences)]
    return text


def GetLexRankSummary(filename, nsentences):
    data = getPDFText2(filename)
    parser = PlaintextParser.from_string(data, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = LexRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")
    text = [a._text for a in summarizer(parser.document, nsentences)]
    return text


def GetLsaSummary(filename, nsentences):
    data = getPDFText2(filename)
    parser = PlaintextParser.from_string(data, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")
    text = [a._text for a in summarizer(parser.document, nsentences)]
    return text


def GetLuhnSummary(filename, nsentences):
    data = getPDFText2(filename)
    parser = PlaintextParser.from_string(data, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = LuhnSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")
    text = [a._text for a in summarizer(parser.document, nsentences)]
    return text


def GetKLSummary(filename, nsentences):
    data = getPDFText2(filename)
    parser = PlaintextParser.from_string(data, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = KLSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")
    text = [a._text for a in summarizer(parser.document, nsentences)]
    return text


ALGORITHMS = {
    "TextRank": GetTextRankSummary,
    "LexRank": GetLexRankSummary,
    "LSA": GetLsaSummary,
    "Luhn": GetLuhnSummary,
    "KLSum": GetKLSummary,
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
        self.summarybox = tk.Text(master=self.middle)
        vertical_scroll = ttk.Scrollbar(
            self.middle, orient="vertical", command=self.summarybox.yview
        )
        self.summarybox.configure(
            yscrollcommand=vertical_scroll.set,
        )
        vertical_scroll.pack(side=tk.RIGHT, fill=tk.BOTH)
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
        self.kc = KanoonCrawler()
        self.kc.LoadCourts()
        self.clicked = tk.StringVar()
        self.clicked.set(options[0])
        algos = tk.OptionMenu(self.right, self.clicked, *options)
        nsentences = tk.Entry(self.right, width=2)
        gensummary = tk.Button(
            master=self.right, text="Get Summary", command=partial(self.generate_summary, nsentences)
        )
        courts = []
        for court in self.kc.Courts:
            courts.append(court.full_name)
        selection = tk.StringVar()
        selection.set(courts[0])
        tk.Label(master=self.right, text="\nInput Document:  ").grid(row=1, column=0, sticky="ew")
        openpdfbutton.grid(row=2, column=0, sticky="ew")
        closepdfbutton.grid(row=2, column=1, sticky="ew")
        tk.Label(master=self.right, text="\nSummary Generation: ").grid(row=3, column=0, sticky="ew")
        algos.grid(row=4, column=0, sticky="ew")
        tk.Label(master=self.right, text="Select Algorithm").grid(row=4, column=1, sticky="ew")
        nsentences.grid(row=5, column=0, sticky="ew")
        tk.Label(master=self.right, text="# of sentences in summary").grid(row=5, column=1, sticky="ew")
        gensummary.grid(row=6, column=0, sticky="ew", columnspan=3)
        self.right.grid(row=0, column=2, sticky="nsew")

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
            self.summarybox.insert("%f" % (i+1), text[i])
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


app = Application("Kanoon Software")
app.mainloop()
