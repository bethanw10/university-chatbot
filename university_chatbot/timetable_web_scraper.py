'''
Questions-
When's the next lecture/workshop/assessment for computer science?
What have I got next for 4CS001
What lectures are tomorrow?
what do I have week 2?

Activities  -
Lecture
Tutorial
Workshop
Assessment
Resit Assessment

weeks are written as
5, 6 ~ 12
'''
import time
import urllib

import gc

import bs4
import pandas as pd
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from university_chatbot import *

week_one = date(2017, 8, 28)

courses = {
    "BEng (Hons) Civil and Transportation Engineering": [
        "4CV003", "4CV010", "4CV002", "4CV005", "4CV001", "4CV009", "5CN022", "5CV005", "5CV001", "5CV003", "5CV006",
        "5CV009", "6CV011", "6CV013", "6CV005", "6CN020", "6CV003", "6CV008"],
    "BEng(Hons) Civil Engineering": [
        "4CV006", "4CV013", "4CV012", "4CV014", "4CV009", "4CV011", "5CV016", "5CV017", "5CV002", "5CV010", "5CV004",
        "5CV015", "6CV020", "6CV021", "6CV006", "6CV009", "6CV018", "6CV019"],
    "BSc (Hons) Building Surveying": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN029", "5CN038", "5CN007",
        "5CN010", "6CN010", "6CN019", "6CN002", "6CN011", "6CN007", "6CN006", "6CN012""4CN002", "4CN016", "4CN006",
        "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN029", "5CN038", "5CN007", "5CN010", "5CN004", "6CN010",
        "6CN019", "6CN002", "6CN011", "6CN007", "6CN006", "6CN012"],
    "BSc(Hons)  Interior Architecture and Property Development": [
        "4AT003", "4AT005", "4AT002", "4AT004", "4AT009", "4AT019", "5AT016", "5AT012", "5CN029", "5AT013", "5AT002",
        "5AT014", "6AT015", "6AT008", "6AT005", "6CN019", "6AT001"],
    "BSc(Hons) Architectural Design Technology": [
        "4AT003", "4AT005", "4AT002", "4AT004", "4AT009", "4AT019", "5AT019", "5AT018", "5CN018", "5AT013", "5AT002",
        "5AT014", "6AT015", "6AT016", "6AT005", "6CN007", "6AT001"],
    "BSc(Hons) Architecture": [
        "4AT014", "4AT016", "4AT017", "4AT018", "4AT015", "5AT021", "5AT024", "5AT022", "5AT020", "5AT023", "6AT009",
        "6AT012", "6AT013", "6AT014", "6AT011"],
    "BSc(Hons) Construction Management": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN002", "5CN010",
        "5CN018", "6CN010", "6CN019", "6CN011", "6CN017", "6CN005", "6CN012", "6CN006""4CN002", "4CN016", "4CN006",
        "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN002", "5CN010", "5CN018", "6CN010", "6CN019",
        "6CN011", "6CN017", "6CN018", "6CN005", "6CN012", "6CN006"],
    "BSc(Hons) Environmental Health": [
        "4EH003", "4EH004", "4EH002", "4EH001", "4EH009", "4HW002", "5EH002", "5EH004", "5EH005", "5EH008", "5EH009",
        "5EH003", "6EH004", "6EH002", "6EH008", "6EH005", "6EH001", "6EH003""4EH003", "4EH004", "4EH002", "4EH001",
        "4EH009", "4HW002", "5EH002", "5EH004", "5EH005", "5EH008", "5EH009", "5EH003", "6EH004", "6EH002", "6EH008",
        "6EH005", "6EH001", "6EH003"],
    "BSc(Hons) Geography, Urban Environments and Climate Change": [
        "4CN002", "4EA003", "4EH001", "4EH002", "4EA001", "4EA002", "5CV003", "5CN018", "5EA001", "5EA003", "5AT024",
        "5EA002", "6EA002", "6AT012", "6CV005", "6EA001", "6CN012", "6EA003", "6EA004"],
    "BSc(Hons) Property Management and Real Estate": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN016", "5CN014",
        "5CN010", "6CN010", "6CN019", "6CN011", "6CN003", "6CN022", "6CN012", "6CN006"],
    "BSc(Hons) Quantity Surveying": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN035", "5CN034",
        "5CN010", "6CN010", "6CN019", "6CN011", "6CN024", "6CN023"],
    "HNC Architectural Studies": [
        "4AT003", "4AT005", "4AT002", "4AT009", "4AT019"],
    "HNC Building Studies": [
        "4CN002", "4CN006", "4CN001", "4CN016", "4CN030", "4CN027"],
    "HND Architectural Design": [
        "4AT003", "4AT005", "4AT002", "4AT004", "4AT009", "4AT019", "5AT018", "5AT019", "5CN018", "5AT013", "5AT002",
        "5AT014"],
    "HND Construction and The Built Environment": [
        "4CN002", "4CN016", "4CN006", "4CN030", "4CN001", "4CN027", "5CN001", "5CN022", "5CN038", "5CN029", "5CN007",
        "5CN010"],
    "MSc Building Information Modelling for Integrated Construction": [
        "7AT003", "7ET022", "7AT005", "7AT001", "7AT006", "7ET023", "7CN003", "7CN010", "7CV003", "7CV004", "7CV007",
        "7EA006", "7EA007", "7EA016", "7EH004", "7AT002""7AT003", "7AT005", "7AT006", "7CN003", "7CN010", "7CV003",
        "7CV004", "7CV007", "7EA006", "7EA007", "7EA016", "7EH004", "7AT002"],
    "MSc Civil Engineering Management": [
        "7CV006",
        "7ET022",
        "7CV005",
        "7CV007",
        "7CN005",
        "7CV004",
        "7ET023"],
    "MSc Construction Law and Dispute Resolution": [
        "7CN013", "7CN011", "7CN017", "7CN012", "7CN001", "7CN010", "7CN008", "7ET022", "7ET023""7CN013", "7CN011",
        "7CN017", "7CN012", "7CN001", "7CN010", "7CN008", "7ET022", "7ET023"],
    "MSc Construction Project Management": [
        "7CN004", "7ET022", "7CN001", "7CN013", "7CN005", "7CN003", "7CN006", "7ET023"],
    "MSc Environmental Technology": [
        "7EA014", "7EA015", "7EA011", "7EH002", "7EA001", "7EA012", "7EA007", "7EA013", "7AB001"],
    "MSc Oil and Gas Management": [
        "7CM002", "7EA018", "7LW002", "7BE002", "7EA017", "7EA019", "7EA006", "7MG001"],
    "MSc Programme and Project Management": [
        "7CN015", "7ET022", "7CN017", "7HR006", "7CN018", "7CN016", "7ET023"],
    "Postgraduate Certificate Building Information Modelling": [
        "7AT003", "7AT007", "7AT006"],
    "Postgraduate Certificate Construction Law and Dispute Resolution": [
        "7CN011", "7CN010", "7CN008", "7CN012", "7CN013", "7CN017""7CN011", "7CN010", "7CN008", "7CN012", "7CN013",
        "7CN017"],
    "Postgraduate Certificate Project and Programme Management": [
        "7CN015", "7CN018", "7HR006"],
    "BEng (Hons) Aerospace Engineering": [
        "4MA007", "4MA008", "4MA009", "4MA010", "4MA011", "5MA005", "5MA006", "5MA007", "5MA009", "5MA010", "5MA016",
        "6MA008", "6MA009", "6MA011", "6MA012", "6MA017"],
    "BEng (Hons) Automotive Engineering": [
        "4MA007", "4MA008", "4MA013", "4MA014", "4MA015", "5MA005", "5MA006", "5MA007", "5MA017", "5MA018", "6MA010",
        "6MA011", "6MA019", "6MA020", "6MA017"],
    "BEng (Hons) Electronics and Telecommunications Engineering": [
        "4MA007", "4MA008", "4MA020", "4MA022", "4MA021", "5MA019", "5MA021", "5MA022", "5MA023", "5MA020", "5MA016",
        "6MA011", "6MA021", "6MA022", "6MA023", "6MA017""4MA007", "4MA008", "4MA020", "4MA022", "4MA021", "5MA019",
        "5MA021", "5MA022", "5MA023", "5MA020", "5MA016", "6MA011", "6MA021", "6MA022", "6MA023", "6MA017"],
    "BEng (Hons) Mechanical Engineering": [
        "4MA007", "4MA008", "4MA017", "4MA018", "4MA016", "5MA006", "5MA008", "5MA013", "5MA014", "5MA011", "6MA011",
        "6MA014", "6MA016", "6MA018", "6MA017"],
    "BEng (Hons) Mechatronics Engineering": [
        "4MA007", "4MA008", "4MA017", "4MA020", "4MA021", "5MA013", "5MA019", "5MA021", "5MA023", "5MA020", "5MA016",
        "6MA011", "6MA021", "6MA025", "6MA026", "6MA017"],
    "BEng (Hons) Motorsport Engineering": [
        "4MA007", "4MA008", "4MA014", "4MA019", "4MA015", "5MA005", "5MA006", "5MA007", "5MA015", "5MA012", "6MA010",
        "6MA011", "6MA015", "6MA013", "6MA017"],
    "MEng (Hons) Aerospace Engineering": [
        "4MA007", "4MA008", "4MA009", "4MA010", "4MA011", "5MA005", "5MA006", "5MA007", "5MA009", "5MA010", "5MA016",
        "6MA008", "6MA009", "6MA011", "6MA012", "6MA017", "7MA004", "7MA005", "7MA006", "7MA010", "7MA012""4MA007",
        "4MA008", "4MA009", "4MA010", "4MA011", "5MA005", "5MA006", "5MA007", "5MA009", "5MA010", "5MA016", "6MA008",
        "6MA009", "6MA011", "6MA012", "6MA017", "7MA004", "7MA005", "7MA006", "7MA010", "7MA012"],
    "MEng (Hons) Automotive Engineering": [
        "4MA007", "4MA008", "4MA013", "4MA014", "4MA015", "5MA005", "5MA006", "5MA007", "5MA017", "5MA018", "6MA010",
        "6MA011", "6MA019", "6MA020", "6MA017", "7MA005", "7MA006", "7MA007", "7MA010", "7MA012"],
    "MEng (Hons) Electronic and Telecommunications Engineering": [
        "4MA007", "4MA008", "4MA020", "4MA022", "4MA021", "5MA019", "5MA021", "5MA022", "5MA023", "5MA020", "5MA016",
        "6MA011", "6MA021", "6MA022", "6MA023", "6MA017", "7MA011", "7MA015", "7MA016", "7MA017", "7MA012"],
    "MEng (Hons) Mechanical Engineering": [
        "4MA007", "4MA008", "4MA017", "4MA018", "4MA016", "5MA006", "5MA008", "5MA013", "5MA014", "5MA011", "6MA018",
        "6MA016", "6MA011", "6MA014", "6MA017", "7MA010", "7MA011", "7MA012", "7MA013", "7MA018"],
    "MEng (Hons) Mechatronics Engineering": [
        "4MA007", "4MA008", "4MA017", "4MA020", "4MA021", "5MA013", "5MA019", "5MA021", "5MA023", "5MA020", "5MA016",
        "6MA011", "6MA021", "6MA025", "6MA026", "6MA017", "7MA011", "7MA014", "7MA016", "7MA017", "7MA012"],
    "MEng (Hons) Motorsport Engineering": [
        "4MA007", "4MA008", "4MA014", "4MA019", "4MA015", "5MA005", "5MA006", "5MA007", "5MA015", "5MA012", "6MA010",
        "6MA011", "6MA013", "6MA015", "6MA017", "7MA006", "7MA007", "7MA009", "7MA010", "7MA012"],
    "MSc Advanced Technology Management (Engineering Analysis)": [
        "7ET022", "7CM002", "7AT004", "7CM003", "7CM001", "7ET032", "7ET023"],
    "MSc Advanced Technology Management (Manufacturing)": [
        "7ET022", "7CM002", "7ET019", "7CM003", "7AT004", "7ET020"],
    "7ET023""MSc Advanced Technology Management (Sustainability)": [
        "7ET022", "7CM002", "7CM004", "7CM003", "7AT004",
        "7ET026", "7ET023"],

    "MSc Manufacturing Engineering": [
        "7ET022", "7CM004", "7ET019", "7MA001", "7AT004", "7CM003", "7ET023"],
    "Postgraduate Certificate Manufacturing Engineering": [
        "7ET019", "7AT004", "7MA001"],
    "BSc (Hons) Computer Science with Secondary Education (QTS)": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4CS016", "4SE001", "5CS019", "5CS021", "5CI022", "5SE001", "5SE002",
        "5CS016", "5CS028", "6CS020", "6SE007", "6SE008", "6CS014"],
    "BSc (Hons) Industrial Mathematics": [
        "4MM001", "4MM009", "4MM010", "4MM002", "4MM003", "4MM004", "5ET005", "5ET009", "5MM001", "5MM012", "5MM013",
        "5MM003", "5MM009", "6ET006", "6MM014", "6MM003", "6ET002", "6MM012", "6MM013", "6MM010", "6MM002"],
    "BSc (Hons) Mathematics with Secondary Education (QTS)": [
        "4MM001", "4MM002", "4MM010", "4MM004", "4MM003", "4MM009", "4SE001", "5MM001", "5MM011", "5MM012", "5SE001",
        "5SE002", "5MM003", "5SE003", "6MM003", "6MM011", "6MM014", "6SE007", "6SE008"],
    "BSc(Hons) Business Intelligence": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4MM015", "4CI017", "5CI021", "5CI022", "5CS030", "5CS024", "5MM014",
        "5MM015", "6CS019", "6CS005", "6MM017", "6CS012", "6MM016"],
    "BSc(Hons) Cloud Computing": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4CS012", "4CS016", "5CS032", "5CI022", "5CS030", "5CS022", "5CS031",
        "5CS024", "5CS016", "6CS023", "6CS026", "6CS005", "6CS030", "6CS029"],
    "BSc(Hons) Computer Science":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CI022", "5CS022", "5CS020", "5CS024", "5CS016",
         "6CS014", "6CS005", "6CS012", "6CS001", "6CS007", "6CS008", "6CS003"],
    "BSc(Hons) Computer Science (Games Development)":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CS025", "5CS027", "5CS020", "5CS024", "5CS016",
         "6CS013", "6CS004", "6CS005", "6CS001", "6CS012", "6CS007"],
    "BSc(Hons) Computer Science (Software Engineering)":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CI022", "5CS022", "5CS020", "5CS024",
         "5CS016", "6CS001", "6CS005", "6CS002", "6CS027", "6CS017"],
    "BSc(Hons) Computer Science (Smart Technologies)": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016", "5CS026", "5CS032", "5CS023", "5CS028", "5CS029",
        "5CS024", "5CS016", "6CS014", "6CS026", "6CS012", "6CS027", "6CS015"],
    "BSc(Hons) Computer Systems Engineering": [
        "4CS001", "4CC002", "4CI013", "4CS011", "4CC016", "4CC001", "5CS015", "5CC002", "5CI017", "5CC004", "5CS014",
        "5CS012", "5CS016", "6CC002", "6CC009", "6CI007", "6CC004", "6CS007"],
    "BSc(Hons) Computing and Information Technology": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4CS012", "4CS016", "5CS023", "5CI022", "5CS032", "5CI023", "5CS031",
        "5CS016", "5CS024", "6CS022", "6CS013", "6CS026", "6CS028", "6CS029"],
    "BSc(Hons) Cybersecurity": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4MM015", "4CS012", "5CS032", "5CI021", "5CS018", "5CS031", "5CS035",
        "5CS024", "5CS016", "6CS021", "6CS032", "6CS031", "6CS010", "6CS027"],
    "BSc(Hons) Data Science": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4MM014", "4CS016", "5CI021", "5CI022", "5CS021", "5CS022", "5CS024",
        "5MM015", "6CS018", "6CS005", "6MM017", "6CS012", "6CS030"],
    "BSc(Hons) Mathematical Sciences": [
        "4MM001", "4MM009", "4MM010", "4MM002", "4MM003", "4MM004", "5MM001", "5MM005", "5MM012", "5MM009", "5MM013",
        "5MM002", "5MM003", "6MM005", "6MM013", "6MM003", "6MM004", "6MM010", "6MM012", "6MM014"],
    "BSc(Hons) Mathematics": [
        "4MM001", "4MM009", "4MM010", "4MM002", "4MM003", "4MM004", "5MM001", "5MM011", "5MM005", "5MM012", "5MM002",
        "5MM003""5MM009", "5MM013", "6MM003", "6MM011", "6MM005", "6MM013", "6MM014", "6MM002", "6MM009", "6MM004",
        "6MM010", "6MM014"],
    "HND Computing": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4CS012", "4CS016", "5CS023", "5CI022", "5CS032", "5CI023", "5CS031",
        "5CS034"],
    "HND Information Technology": [
        "4CS001", "4CS015", "4CI018", "4CS014", "4CI017", "4MM015", "5CI021", "5CS018", "5CI022", "5CS034", "5CS035",
        "5CS023"],
    "HND Mathematics and Computing": [
        "4CS001", "4CS015", "4MM001", "4MM003", "4MM004", "4CS016", "5CS023", "5MM001", "5CI022", "5CS032", "5MM013",
        "5MM014", "5CI023", "5CS031"],
    "MSc Computer Science": [
        "7ET023", "7CC009", "7CC003", "7CI019", "7CC005", "7CC012", "7CC002", "7CS013"],
    "MSc Information Technology": [
        "7ET023", "7CC009", "7CS001", "7CI006", "7CC001", "7CC006", "7CC002", "7CS013"],
    "MSc Information Technology Management": [
        "7ET023", "7CC009", "7CI006", "7CI017", "7CI008", "7CI011", "7CI014"],
    "MSc Mathematics": [
        "7MM006", "7MM007", "7MM008", "7MM005", "7MM009", "7MM010", "7MM011"],
    "MSc Web and Mobile Application Development": [
        "7CC009", "7CC010", "7CC011", "7CC005", "7CC012", "7CC002", "7CS013", "7ET023"],
    "Postgraduate Certificate Mathematics": [
        "7MM007", "7MM008", "7MM005", "7MM006", "7MM009"],
    "Postgraduate Certificate Web and Mobile Application Development": [
        "7CC009", "7CC010", "7CC011", "7CC005", "7CC012", "7CC002", "7CS013"],
    "BSc(Hons) Pharmaceutical Science": [
        "4PY011", "4BM004", "4PY012", "4PY009", "4PY008", "4PY013"],
    "BSc(Hons) Pharmacology": [
        "4PY014", "4BM004", "4PY012", "4PY013", "4PY008", "4PY009", "5BC001", "5PY017", "5PY010", "5PY016", "5PY018",
        "5PY024", "6PY004", "6BC002", "6PY002", "6PY007", "6PY006"],
    "HND Pharmaceutical Science": [
        "4PY011", "4PY012", "4BM004", "4PY013", "4PY008", "4PY009", "5BC001", "5BC002", "5PY017", "5PY015", "5PY010",
        "5PY014"],
    "Master of Pharmacy (MPharm Hons)": [
        "4PY019", "5PY022", "6PY011", "7PY023"],
    "MSc Pharmaceutical Science (Drug Discovery and Design)": [
        "7PY011", "7PY003", "7PY009", "7PY007", "7PY014", "7PY015", "7PY017", "7PY007"],
    "MSc Pharmaceutical Science (Pharmacological Sciences)": [
        "7PY011", "7PY003", "7PY009", "7PY014", "7PY010", "7PY013", "7PY007"],
    "MSci (Hons) Pharmaceutical Science": [
        "4PY011", "4BM004", "4PY012", "4PY013", "4PY008", "4PY009", "5BC001", "5PY017", "5PY010", "5PY015", "5PY023",
        "5PY014", "6PY004", "6PY005", "6PY002", "6BC003", "6PY006", "7PY011", "7PY003", "7PY026", "7PY025", "7PY013",
        "7PY014"],
    "MSci (Hons) Pharmacology": [
        "4PY014", "4BM004", "4PY012", "4PY013", "4PY008", "4PY009", "5BC001", "5PY017", "5PY010", "5PY016", "5PY018",
        "5PY024", "6PY004", "6BC002", "6PY002", "6PY007", "6PY006", "7PY011", "7PY010", "7PY027", "7PY024", "7PY013",
        "7PY026"],
    "Postgraduate Certificate in Prescribing Studies": [
        "7PY019", "7NH015", "7PY013"],
    "BMed Sci (Hons) Medical Science": [
        "4BM003", "4BM004", "4BM011", "4PY013", "4BM005", "4PY009", "5BM009", "5BM010", "5BM033", "5BM013", "5BM019",
        "5PY010", "6BM008", "6BM017", "6BM010", "6BM009", "6BM014"],
    "BSc (Hons) Biomedical Science (Pathology Laboratory Based)": [
        "4BM003", "4BM004", "4PY013", "4BM013", "4BM007", "4BM012", "5BM009", "5BM008", "5BM004", "5BM006", "5BM027",
        "5BM028", "6BM006", "6BM008", "6BM010", "6BM009", "6BM014"],
    "BSc (Hons) Chemical Engineering with Chemistry": [
        "4ET011", "4ET005", "4CH003", "4ET004", "4ET012", "4CH002", "5ET030", "5ET032", "5CH003", "5ET015", "5ET014",
        "5CH001", "6ET025", "6CH003", "6CH006", "6CH004"],
    "6ET012""BSc (Hons) Chemical Engineering with Pharmaceutical Science": [
        "4ET011", "4ET005", "4PY011", "4ET004", "4ET012", "4PY013", "5ET030", "5ET032", "5PY015", "5ET015", "5ET014",
        "5PY014", "6ET025", "6PY005", "6BC003", "6ET006", "6ET013",
        "6ET012"],
    "BSc (Hons) Chemistry with Secondary Education (QTS)": [
        "4CH006", "4CH001", "4CH002", "4CH003", "4CH004", "4CH005", "5CH003", "5CH004", "5CH005", "5CH001", "5CH002",
        "5CH006", "6CH001", "6SE001", "6SE002", "6CH002", "6SE007"],
    "BSc (Hons) Forensic Science and Criminology": [
        "4CJ005", "4FS002", "4CJ003", "4FS005", "4PY013", "4CJ002", "5FS001", "5CJ002", "5LW002", "5FS005", "5CJ003",
        "5FS002", "6AB003", "6FS003", "6CJ006", "6FS004", "6CJ005""4CJ005", "4FS002", "4CJ003", "4FS005", "4PY013",
        "4CJ002", "5FS001", "5CJ002", "5LW002", "5FS005", "5CJ003", "5FS002", "6AB003", "6FS003", "6CJ006", "6FS004",
        "6CJ005"],
    "BSc (Hons) Healthcare Science (Cardiac Physiology)": [
        "4BM003", "4BM004", "4BM014", "4BM005", "4BM009", "4PY013", "5BM014", "5BM021", "5BM017", "5BM020", "5BM019",
        "5BM034", "6BM013", "6BM014", "6BM019", "6BM026"],
    "BSc (Hons) Healthcare Science (Physiological Sciences)": [
        "4BM003", "4BM004", "4BM014", "4BM005", "4BM009", "4PY013", "5BM014", "5BM021", "5BM020", "5BM017", "5BM018",
        "5BM019""5BM034", "5BM035", "6BM013", "6BM014", "6BM019", "6BM020", "6BM026", "6BM027"],
    "BSc (Hons) Healthcare Science (Respiratory and Sleep Physiology)": [
        "4BM003", "4BM004", "4BM014", "4BM005", "4BM009", "4PY013", "5BM014", "5BM021", "5BM018", "5BM020", "5BM035",
        "5BM019", "6BM013", "6BM014", "6BM020", "6BM026"],
    "BSc (Hons) Medical Physiology and Diagnostics": [
        "4BM003", "4BM004", "4BM014", "4BM005", "4BM009", "4PY013", "5BM020", "5BM009", "5BM038", "5BM040""5BM039",
        "5BM041", "5BM019", "5BM021", "6BM014", "6BM017", "6BM028", "6BM029", "6BM026", "6BM030", "6BM031", "6BM027"],
    "BSc (Hons) Physics": [
        "4AP001", "4MM011", "4MM012", "4AP003", "4AP004", "4AP006", "5AP001", "5AP002", "5AP003", "5AP004", "5AP005",
        "5AP006", "6AP001", "6AP002", "6AP003", "6AP007", "6AP008", "6AP009"],
    "BSc (Hons) Physics with Secondary Education (QTS)": [
        "4AP001", "4MM011", "4MM012", "4AP004", "4AP003", "4AP006", "5AP001", "5AP002", "5AP003", "5AP004", "5AP006",
        "5SE003", "6AP001", "6SE001", "6SE007", "6SE008"],
    "BSc(Hons) Animal Behaviour and Wildlife Conservation": [
        "4AB009", "4AB010", "4AB013", "4AB011", "4AB014", "4AB015", "5AB009", "5AB013", "5AB015", "5AB010", "5AB014",
        "5AB007", "5AB011", "5AB016""5BM012", "5WL001", "5WL002", "6AB003", "6AB004", "6AB008", "6AB007", "6AB005",
        "6AB009", "6AB010", "6WL001"],
    "BSc(Hons) Biochemistry": [
        "4AB008", "4BM004", "4BM005", "4PY013", "4BC001", "4BC002", "4PY009", "4BM006", "5BC001", "5BC002", "5BC003",
        "5AB008", "5BC004", "5PY010", "5BM006""6AB003", "6BC001", "6BC002", "6BC003", "6PY006", "6BM009"],
    "BSc(Hons) Biological Sciences": [
        "4AB008", "4AB007", "4PY013", "4AB012", "4BC001", "4BC002", "4AB010", "4AB013", "4BM004", "4WL002",
        "4WL003""4AB015", "4BM008", "4AB014", "4WL002", "4WL003", "5BC001", "5BC003", "5AB008", "5AB012", "5BC002",
        "5AB009", "5AB015", "5WL001", "5WL002", "5AB010", "5BM012", "5WL001", "5WL002""6AB003", "6AB001", "6AB002",
        "6BM015", "6AB008", "6AB005", "6BC002", "6WL001", "6BM010", "6BM016", "6AB005", "6WL001"],
    "BSc(Hons) Biomedical Science": [
        "4BM003", "4BM004", "4BM011", "4PY013", "4BM005", "4BM006", "5BM004", "5BM005", "5BM009", "5BM006", "5BM007",
        "5BM008", "6BM006", "6BM008", "6BM010", "6BM009", "6BM014"],
    "BSc(Hons) Biotechnology": [
        "4AB008",
        "4AB007",
        "4AB012",
        "4BM006",
        "4PY013",
        "4BC001",
        "4BC002",
        "4WL002",
        "4WL003",
        "5BC001",
        "5BC003",
        "5PY017",
        "5BC002",
        "5WL001",
        "5WL002",
        "5AB008",
        "5AB012",
        "5AB025",
        "6AB003",
        "6AB001",
        "6BC002",
        "6AB002",
        "6AB006"],
    "BSc(Hons) Chemistry": [
        "4CH006", "4CH001", "4CH002", "4CH003", "4CH004", "4CH005", "5CH003", "5CH004", "5CH005", "5CH001", "5CH002",
        "5CH006", "6CH001", "6CH003", "6CH005", "6CH002", "6CH004", "6CH006"],
    "BSc(Hons) Forensic Science": [
        "4FS002", "4FS007", "4PY013", "4FS004", "4FS005", "4BC001", "4BC002", "5FS002", "5FS003", "5FS001", "5FS004",
        "5FS005", "5FS006", "6AB003", "6FS003", "6FS002", "6FS004", "6FS005"],
    "BSc(Hons) Genetics and Molecular Biology": [
        "4AB008", "4AB007", "4BM005", "4BM006", "4PY013", "4BC001", "4BC002", "4WL002", "4WL003", "5BC001", "5BC002",
        "5BC003", "5AB008", "5BC004", "5BM012", "6AB003", "6BC001", "6BC002", "6BM016", "6AB002"],
    "BSc(Hons) Human Biology": [
        "4SH001", "4BM004", "4BM003", "4BM008", "4BM006", "4PY013", "5BM009", "5BM010", "5BM012", "5BM013", "5BM011",
        "5FS002", "6BM015", "6BM017", "6BM016", "6BM018", "6BM014"],
    "BSc(Hons) Microbiology": [
        "4AB008", "4AB007", "4BC001", "4BC002", "4WL002", "4WL003", "4AB012", "4BM006", "4PY013", "5BC001", "5BC003",
        "5PY017", "5BC002", "5WL001", "5WL002", "5AB008", "5AB012", "5AB025", "6AB003", "6AB001", "6EH005", "6BM010",
        "6AB006"],
    "HNC Chemistry": [
        "4CH006", "4CH001", "4CH002", "4CH003", "4CH004", "4CH005", "4CH006", "4CH001", "4CH002", "4CH003", "4CH004",
        "4CH005"],
    "HND Animal Behaviour and Wildlife Conservation": [
        "4AB009", "4AB010", "4AB013", "4AB011", "4AB014", "4AB015", "5AB009", "5AB013", "5AB018", "5AB010", "5AB014",
        "5AB007"],
    "HND Applied Biology": [
        "4AB008", "4AB007", "4PY013", "4AB012", "4AB010", "4BC001", "4WL002", "4BC002", "4WL003", "4AB014", "4PY009",
        "4BM006", "4WL002", "4WL003""5BC001", "5BC003", "5AB008", "5AB007", "5AB009", "5AB015", "5BC002", "5WL001",
        "5WL002", "5BC004", "5AB012", "5PY010", "5BM006", "5AB010", "5BM012", "5EH001", "5WL001", "5WL002", "4AB008",
        "4AB007""4PY013", "4AB012", "4AB010", "4BC001", "4WL002", "4BC002", "4WL003", "4AB014", "4PY009", "4BM006",
        "4WL002", "4WL003", "5BC001", "5BC003", "5AB008", "5AB007", "5AB009", "5AB015", "5BC002", "5WL001""5WL002",
        "5BC004", "5AB012", "5PY010", "5BM006", "5AB010", "5BM012", "5EH001", "5WL001", "5WL002"],
    "HND Biomedical Science": [
        "4BM011", "4BM003", "4BM004", "4BM005", "4BM006", "4PY013", "5BM004", "5BM005", "5BM009", "5BM006", "5BM008",
        "5BM016"],
    "HND Chemistry": [
        "4CH006", "4CH001", "4CH002", "4CH003", "4CH004", "4CH005", "5CH003", "5CH004", "5AB011", "5CH001", "5CH002",
        "5CH006""4CH006", "4CH001", "4CH002", "4CH003", "4CH004", "4CH005", "5CH003", "5CH004", "5AB011", "5CH001",
        "5CH002", "5CH006"],
    "HND: Forensic Science": [
        "4FS002", "4FS007", "4BC001", "4BC002", "4FS004", "4FS005", "4PY013", "5FS002", "5FS003", "5FS001", "5FS004",
        "5FS005", "5FS006""4FS002", "4FS007", "4BC001", "4BC002", "4FS004", "4FS005", "4PY013", "5FS002", "5FS003",
        "5FS001", "5FS004", "5FS005", "5FS006"],
    "Masters in Biology (MBiol)": [
        "4AB007", "4AB008", "4AB010", "4AB013", "4BC001", "4BC002", "4BM004", "4AB012", "4PY013""4AB014", "4AB015",
        "4BM006", "4BM008", "5BC001", "5BC003", "5AB009", "5AB015", "5BC002", "5PY017", "5AB008", "5AB012", "5AB010",
        "5BM012", "5EH001", "6AB003", "6AB001", "6EH005""6BC002", "6AB008", "6AB002", "6AB006", "6AB009", "6BM010",
        "6BM016", "7FS014", "7AB004", "7BC002", "7AB006", "7AB001", "7BC003", "7BC004", "4AB007", "4AB008""4AB010",
        "4AB013", "4BC001", "4BC002", "4BM004", "4AB012", "4PY013", "4AB014", "4AB015", "4BM006", "4BM008", "5BC001",
        "5BC003", "5AB009", "5AB015", "5BC002", "5PY017", "5AB008", "5AB012""5AB010", "5BM012", "5EH001", "6AB003",
        "6AB001", "6EH005", "6BC002", "6AB008", "6AB002", "6AB006", "6AB009", "6BM010", "6BM016", "7FS014", "7AB004",
        "7BC002", "7AB006""7AB001", "7BC003", "7BC004"],
    "MChem (Hons) Masters in Chemistry": [
        "4CH006", "4CH001", "4CH003", "4CH002", "4CH004", "4CH005", "5CH003", "5CH004", "5CH005", "5CH001", "5CH002",
        "5CH006", "6CH001", "6CH003", "6CH005", "6CH002", "6CH004", "6CH006", "7CH001", "7CH005", "7CH007", "7CH003",
        "7CH006""4CH006", "4CH001", "4CH003", "4CH002", "4CH004", "4CH005", "5CH003", "5CH004", "5AB007", "5AB011",
        "5CH001", "5CH002", "5CH006", "6CH001", "6CH003", "6CH005", "6CH002", "6CH004", "6CH006", "7CH001", "7CH005",
        "7CH007", "7CH003", "7CH006"],
    "MSc Applied Microbiology and Biotechnology": [
        "7AB004", "7AB006", "7BC002", "7AB002", "7AB007", "7AB001", "7BC003", "7AB005", "7AB004", "7AB006", "7BC002",
        "7AB002", "7AB007", "7AB003", "7AB008", "7AB005"],
    "MSc Biomedical Science": [
        "7BM003", "7BC002", "7BM010", "7BM004", "7BM002", "7BM001", "7BM006", "7BM007", "7BM005"],
    "MSc Biomedical Science (Cellular Pathology)": [
        "7BM003", "7BC002", "7BM011", "7BM004", "7BM006", "7BM008", "7BM002", "7BM003", "7BC002", "7BM011", "7BM004",
        "7BM006", "7BM009", "7BM002"],
    "MSc Biomedical Science (Clinical Biochemistry)": [
        "7BM003", "7BC002", "7BM011", "7BM001", "7BM004", "7BM008", "7BM002", "7BM003", "7BC002", "7BM011", "7BM001",
        "7BM004", "7BM009", "7BM002"],
    "MSc Biomedical Science (Haematology)": [
        "7BM003", "7BC002", "7BM011", "7BM007", "7BM004", "7BM008", "7BM002", "7BM003", "7BC002", "7BM011", "7BM007",
        "7BM004", "7BM009", "7BM002"],
    "MSc Biomedical Science (Medical Microbiology)": [
        "7BM003", "7BC002", "7BM011", "7BM004", "7BM005", "7BM008", "7BM002", "7BM003", "7BC002", "7BM011", "7BM004",
        "7BM005", "7BM009", "7BM002"],
    "MSc Chemistry": [
        "7CH009", "7CH005", "7CH007", "7CH003", "7CH006", "7CH002"],
    "MSc Fire Scene Investigation": [
        "7FS005", "7FS006", "7FS008", "7FS009", "7AB007", "7FS007", "7AB005"],
    "MSc Forensic Genetics and Human Identification": [
        "7FS002", "7FS004", "7BC002", "7FS003", "7FS001", "7AB007", "7AB005"],
    "MSc Instrumental Chemical Analysis": [
        "7CH006", "7CH011", "7PY003", "7CH002", "7CH005", "7CH007", "7CH003", "7CH006"],
    "MSc Molecular Biology with Bioinformatics": [
        "7CS001", "7BC002", "7CI006", "7BC003", "7AB002", "7AB007", "7AB005"],
    "MSc Wildlife Conservation": [
        "7AB012", "7AB009", "7AB011", "7AB015", "7AB013", "7AB010", "7AB014"],
    "MSci (Hons) Animal Behaviour and Wildlife Conservation": [
        "4AB009", "4AB010", "4AB013", "4AB011", "4AB014", "4AB015", "5AB009", "5AB013", "5AB015", "5AB010", "5AB014",
        "5AB007", "5AB011", "5AB016", "5BM012", "6AB003", "6AB004", "6AB008", "6AB007", "6AB005""6AB009", "6AB010",
        "7AB009", "7AB011", "7AB010", "7AB014", "7FS014", "4AB009", "4AB010", "4AB013", "4AB011", "4AB014", "4AB015",
        "5AB009", "5AB013", "5AB015", "5AB010", "5AB014", "5AB007", "5AB011", "5AB016", "5BM012", "6AB003", "6AB004",
        "6AB008", "6AB007""6AB005", "6AB009", "6AB010", "7AB009", "7AB011", "7AB010", "7AB014", "7FS014"],
    "MSci (Hons) Molecular Bioscience": [
        "4AB008", "4PY013", "4BM005", "4BC001", "4BC002", "4AB007", "4BM004", "4PY009", "4BM006", "5BC001", "5BC002",
        "5BC003", "5BC004""5AB008", "5BM012", "5BM006", "5PY010", "6AB003", "6BC001", "6BC002", "6AB002", "6BC003",
        "6BM016", "6PY006", "6BM009", "7FS014", "7BC002", "7CS001", "7BC003", "7AB002"],
    "Professional Doctorate in Biomedical Science": [
        "8BM001", "8BM002", "8BM003", "8BM004", "8BM005", "8BM006"]
}

extra = {
    "BSc(Hons) Computer Science":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CI022", "5CS022", "5CS020", "5CS024", "5CS016",
         "6CS014", "6CS005", "6CS012", "6CS001", "6CS007", "6CS008", "6CS003"],

    "BSc(Hons) Computer Science (Games Development)":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CS025", "5CS027", "5CS020", "5CS024", "5CS016",
         "6CS013", "6CS004", "6CS005", "6CS001", "6CS012", "6CS007"],

    "BSc(Hons) Computer Science (Software Engineering)":
        ["4CS001", "4CS015", "4CI018", "4CS014", "4MM013", "4CS016",
         "5CS019", "5CS021", "5CI022", "5CS022", "5CS020", "5CS024",
         "5CS016", "6CS001", "6CS005", "6CS002", "6CS027", "6CS017"],
}


def scrape_module_timetable(module_code):
    url = "http://www3.wlv.ac.uk/timetable/testmahi2_1.asp"
    r = requests.post(url, data={'module': module_code})
    page = BeautifulSoup(r.text, "html.parser")

    # Scrape module name
    list_items = page.find_all("li")
    if len(list_items) < 1 or module_code not in list_items[0].text:
        # Invalid module code
        return "", []

    full_module_name = list_items[0].text
    module_name = full_module_name.replace(module_code, "").strip()

    # Scrape module timetable
    timetable = []
    table = page.findAll("table", class_="filtered")

    if len(table) < 1:
        # No timetable found
        return module_name, []

    rows = table[0].find_all('tr')

    for row in rows:
        columns = row.findAll('td')

        # Ignore empty rows
        if not columns:
            continue

        columns = [element.text.strip() for element in columns]
        timetable.append([element for element in columns])

    df = pd.DataFrame(timetable, columns=["Module", "Instance", "Activity", "Weeks", "Day", "Start",
                                          "Finishes", "Campus", "Room", "Lecturer", "Group/cohort details"])
    # Module, Instance, Activity, Weeks, Day, Start, Finishes, Campus, Room, Lecturer, Group/cohort details.
    return module_name, df


def get_week_number(for_date):
    difference = for_date - week_one
    return 1 + (difference.days // 7)


def get_date_by_week_number(week_number, day="Monday"):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if day not in days:
        raise ValueError(day + "is not a valid day of the week")

    day_number = days.index(day)

    start_date = week_one + timedelta(weeks=week_number - 1, days=day_number)
    return start_date


def print_all_activity_dates(module_code):
    _, timetable = scrape_module_timetable(module_code)

    for row in timetable:
        activity = row[2]
        week_ranges = row[3].split(",")
        day = row[4]
        start_time = row[5]

        for week_range in week_ranges:
            # Range of weeks e.g. 6 ~ 16
            if '~' in week_range:
                start_and_end = [number.strip() for number in week_range.split('~')]
                print(start_and_end)

                start = int(start_and_end[0])
                end = int(start_and_end[1])

                for week_number in range(start, end):
                    d = get_date_by_week_number(week_number, day)
                    t = time.strptime(start_time, "%H:%M")
                    dt = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                           hour=t.tm_hour, minute=t.tm_min)
                    print(activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))

            # Single week e.g. 6
            else:
                week_number = int(week_range)
                d = get_date_by_week_number(week_number, day)
                t = time.strptime(start_time, "%H:%M")
                dt = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                       hour=t.tm_hour, minute=t.tm_min)
                print(activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))


def print_next_activity(module_code):
    print("Next activity for " + module_code + ": ")

    now = datetime.datetime.now()
    current_week = get_week_number(now.date())

    _, timetable = scrape_module_timetable(module_code)

    # Loop through each activity to find the first activity that occurs after the current date
    for row in timetable:
        activity = row[2]
        week_ranges = row[3].split(",")
        day = row[4]
        start_time = row[5]

        for week_range in week_ranges:
            # Range of weeks e.g. 6 ~ 16
            if '~' in week_range:
                start_and_end = [number.strip() for number in week_range.split('~')]

                start = int(start_and_end[0])
                end = int(start_and_end[1])

                if end < current_week:
                    continue

                for week_number in range(start, end):
                    if week_number < current_week:
                        continue

                    d = get_date_by_week_number(week_number, day)
                    t = time.strptime(start_time, "%H:%M")
                    dt = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                           hour=t.tm_hour, minute=t.tm_min)

                    if dt > now:
                        print("\t" + activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))
                        return

            # Single week e.g. 6
            else:
                week_number = int(week_range)
                if week_number < current_week:
                    continue

                d = get_date_by_week_number(week_number, day)
                t = time.strptime(start_time, "%H:%M")
                dt = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                       hour=t.tm_hour, minute=t.tm_min)

                if dt > now:
                    print("\t" + activity + ": " + dt.strftime('%d %b %Y %I:%M%p'))
                    return


def import_modules_peewee(courses):
    for course_name, module_codes in courses.items():

        # Save each course
        course, _ = Course.get_or_create(name=course_name)
        print(course.name)

        for module_code in module_codes:

            module_name, timetables = scrape_module_timetable(module_code)

            print(module_code)

            # Skip modules with no timetables
            if len(timetables) == 0:
                continue

            semester = timetables.ix[0, 'Instance']

            # Save module if it doesn't already exist
            module, is_new_module = Module.get_or_create(name=module_name, code=module_code, semester=semester)
            Course_Module.create(module=module, course=course)

            # if not is_new_module:
            # continue

            for index, row in timetables.iterrows():
                timetable = Timetable.create(module=module, activity=row["Activity"], day=row['Day'],
                                             start=row['Start'], finishes=row['Finishes'], campus=row['Campus'],
                                             room=row['Room'], lecturer=row['Lecturer'],
                                             group_details=row['Group/cohort details'])

                # if not is_new:
                #    continue

                week_ranges = row['Weeks'].split(",")
                day = row['Day']

                print(week_ranges)

                # Here we go
                for week_range in week_ranges:

                    # Range of weeks e.g. 6 ~ 16
                    if '~' in week_range:
                        start_and_end = [number.strip() for number in week_range.split('~')]
                        start = int(start_and_end[0])
                        end = int(start_and_end[1])

                        start_week = get_date_by_week_number(start, day)
                        end_week = get_date_by_week_number(end, day)

                    # Single week e.g. 6
                    else:
                        week_number = int(week_range)
                        start_week = end_week = get_date_by_week_number(week_number, day)

                    check = Week_Range.select().where(
                        (
                                Week_Range.timetable == timetable) & Week_Range.start_week == start_week & Week_Range.end_week == end_week)

                    if len(check) != 0:
                        continue

                    Week_Range.get_or_create(timetable=timetable, start_week=start_week, end_week=end_week)


def get_module_codes(url):
    r = requests.get(url, stream=True)

    with open("temp/" + url[-20:], 'wb') as f:
        f.write(r.content)

    with open("temp/" + url[-20:], 'rb') as f:
        parser = PDFParser(f)
        document = PDFDocument(parser)

        # Create PDFResourceManager object that stores shared resources such as fonts or images
        resource_manager = PDFResourceManager()
        la_params = LAParams()

        # Extract the device to page aggregator to get LT object elements
        device = PDFPageAggregator(resource_manager, laparams=la_params)

        # Interpreter needs to be connected to resource manager for shared resources and device
        interpreter = PDFPageInterpreter(resource_manager, device)

        module_codes = []

        for page in PDFPage.create_pages(document):
            first = True

            interpreter.process_page(page)

            # The device renders the layout from interpreter
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    text = lt_obj.get_text().strip()

                    if re.match("\d\w{2}\d{3}", text):
                        if len(text) > 6:
                            print("],")

                            parser.close()
                            return module_codes

                        if not first:
                            print(", ", end=''),
                        else:
                            first = False

                        print("\"" + text + "\"", end=''),
                        # module_codes.append(text)

        # os.remove("temp/temp.pdf")
    parser.close()
    return module_codes


def get_timetables():
    file = open("temp/Faculty of Science and Engineering.html")

    page = BeautifulSoup(file, "html.parser")
    list_items = page.find_all("li")

    # course_modules = {}

    for child in list_items:
        pdf_url = child.find("a", href=True)["href"]
        if "Sandwich" not in child.string \
                and "Foundation" not in child.string \
                and "Top-up" not in child.string \
                and "Top-Up" not in child.string:
            print("\"" + child.string + "\": [")
            get_module_codes(pdf_url)
            gc.collect()


def print_courses():
    courses = Course.select(Course)

    for course in courses:
        print("\"" + course.name + "\",", end='')

        synonym = course.name.replace("(", "").replace(")", "").strip()

        print("\"" + synonym + "\",", end='')

        synonym2 = synonym.replace("MEng", "").replace("BSc", "").replace("BEng", "").replace("HNC", "") \
            .replace("HND", "") \
            .replace("MSci", "").replace("MSc", "").replace("Hons", "").strip()

        print("\"" + synonym2 + "\"")


def print_modules():
    modules = Module.select(Module)

    miss = {"6CS005",
            "5CS025",
            "6CS008",
            "6CS003",
            "5CS027",
            "4MM013",
            "5CS024",
            "6CS002",
            "6CS007",
            "5CS020",
            "4CS014",
            "5CS021",
            "4CS001",
            "4CI018",
            "5CI022",
            "5CS022",
            "4CS016",
            "5CS016",
            "4CS015",
            "5CS019"}

    for module in modules:
        if module.code not in miss:
            print("\"" + module.code + "\",", end='')
            print("\"" + module.name.replace("(", "").replace(")", "") + "\"")


# import_modules_peewee({**courses, **extra})
# import_modules_peewee(extra)
# get_timetables()
# print("done")

# test = {"BEng (Hons) Civil and Transportation Engineering": ["4CV010"]}
# import_modules_peewee(test)

# print(get_date_by_week_number(36))

print(get_date_by_week_number(33))
