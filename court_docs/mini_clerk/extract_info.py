import os
import re
import sys
import tempfile
from difflib import SequenceMatcher
import numpy



from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter

import spacy
from spacy import displacy
from spacy.matcher import Matcher



nlp = spacy.load("en_core_web_md")
def extractpdf(uri):
    debug = 0
    text_pages = []
    page_break = '!##############################!\n\n'
    temp_file = '/data/tmp/temp.txt'
    temp_html_file = '/data/tmp/temp.html'
    original_file = "/data/pdfs/test.pdf"
    test_dir = "/data/pdfs/test2"
    encoding = "utf-8"
    
    #print(fp)
    #for filename in os.listdir(test_dir):
    if(uri.endswith('.pdf') or uri.endswith('.PDF')):
        print(uri)
        with open(uri, "rb") as file:
            laparams = LAParams()
            # Create a PDF resource manager object that stores shared resources.
            rsrcmgr = PDFResourceManager()
            with open(temp_file, 'w', encoding=encoding) as outfp:
            # Create a PDF device object.
                page_written = False
                device = TextConverter(rsrcmgr, outfp, laparams=laparams)
                # Create a PDF interpreter object.
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                # Process each page contained in the document and append page_break.
                for page in PDFPage.get_pages(file):
                    if page_written==False:
                        interpreter.process_page(page)
                        page_written=True
                    else:
                        outfp.write(page_break)
                        interpreter.process_page(page)

        with open(temp_file, 'r') as file:
            pages = file.read().split(page_break)
            #stats = sizeUp(pages, type='pages')
            #print(stats)
            #print(pages)
            escaped_pages = []
            for page in pages:
                escaped_pages.append(str(page))

    #        for i, page in enumerate(pages):
    #           print(i)
            header_predictions = predictHeader(uri, escaped_pages) 
            if(debug==1): print(header_predictions)
            footer_predicitons = predictFooter(uri, escaped_pages)
            if(debug==1): print(footer_predicitons)
            #print(predictFooter(uri, escaped_pages)[0])
    return {'temp_file': temp_file , 'pages': escaped_pages, 'predictions':{'header_predictions': header_predictions, 'footer_predictions': footer_predicitons}}
        

def predictHeader(filename, pages):
    debug = 0
    one_page_predictions = []
    two_page_predictions = []
    matching_length = 8
    if(debug==1): 
        print(len(pages), "pages in total")
    for i, page in enumerate(pages):
        if(debug==1):
            print(i, "page loop")
            print(len(page))
        header_buffer = 500
        if(i+1==len(pages)):
            break
        if(len(page)<header_buffer):
            header_buffer = len(page)
            if(debug==1): print("short page", len(page))
        #if not any(prediction['count'] > 4 for prediction in predictions):
        one_page_prediction = SequenceMatcher(None, pages[i], pages[i+1]).find_longest_match(0, header_buffer, 0, header_buffer)
        if(debug==1): print(pages[i][0:200], "\n", pages[i+1][0:200])
        if(debug==1): print(one_page_prediction.size)

        if(one_page_prediction.size>matching_length):
            #string_present = pages[i].find(pages[0][prediction.a:prediction.a+prediction.size])
            one_page_predicted_header = pages[i][one_page_prediction.a:one_page_prediction.a+one_page_prediction.size]
            if(debug==1): print(one_page_predicted_header)
            if not any(prediction['header'] == one_page_predicted_header for prediction in one_page_predictions):
                one_page_predictions.append({'header': one_page_predicted_header, 'type': 'one-page', 'count': 1})
            else: 
                for prediction in one_page_predictions:
                    #print(prediction)
                    if((prediction['header'] == one_page_predicted_header) & (prediction['type']=='one-page')):
                        prediction['count'] = prediction['count'] + 1
        if(i+2==len(pages)):
            continue
        two_page_prediction = SequenceMatcher(None, pages[i], pages[i+2]).find_longest_match(0, header_buffer, 0, header_buffer)
        if(two_page_prediction.size>matching_length):
            two_page_predicted_header = pages[i][two_page_prediction.a:two_page_prediction.a+two_page_prediction.size]
            #print(two_page_predicted_header)
            if not any(prediction['header'] == two_page_predicted_header for prediction in two_page_predictions):
                two_page_predictions.append({'header': two_page_predicted_header, 'type': 'two-page', 'isEven': (i % 2==0),'count': 1})
            else: 
                for prediction in two_page_predictions:
                    #print(prediction)
                    if(prediction['header'] == two_page_predicted_header and prediction['isEven']==(i % 2==0)):   
                        prediction['count'] = prediction['count'] + 1


    ####Sorting
    length_sorted_one_page_predictions = sorted(one_page_predictions, key = lambda i: (len(i['header'])), reverse=True)
    if(debug==1): print(length_sorted_one_page_predictions)
    for i, prediction in enumerate(length_sorted_one_page_predictions):
        if(i+1==len(length_sorted_one_page_predictions)):
            break
        prediction_greedy_gobble = SequenceMatcher(None, prediction['header'], length_sorted_one_page_predictions[i+1]['header']).find_longest_match()
        if(prediction_greedy_gobble.size/len(prediction['header'])>0.5):
            length_sorted_one_page_predictions[i+1]['count'] = length_sorted_one_page_predictions[i+1]['count'] + prediction['count']
            prediction['count'] = 0
    count_sorted_one_page_predictions = sorted(length_sorted_one_page_predictions, key = lambda i: (i['count']), reverse=True)
    if(len(count_sorted_one_page_predictions)>0):
        if(count_sorted_one_page_predictions[0]['count'] >= (2+len(pages)//4)):
            if(debug==1): print('header', count_sorted_one_page_predictions[0]['header'], count_sorted_one_page_predictions[0]['count'])
    
    length_sorted_two_page_predictions = sorted(two_page_predictions, key = lambda i: (len(i['header'])), reverse=True)
    even_length_sorted_two_page_predictions = []
    odd_length_sorted_two_page_predictions = []
    for prediction in length_sorted_two_page_predictions:
        if prediction['isEven']==True:
            even_length_sorted_two_page_predictions.append(prediction)
        else:
            odd_length_sorted_two_page_predictions.append(prediction)
    if(debug==1): print(length_sorted_two_page_predictions)
    for i, prediction in enumerate(even_length_sorted_two_page_predictions):
        if(i+1>=len(even_length_sorted_two_page_predictions)):
            break
        prediction_greedy_gobble = SequenceMatcher(None, prediction['header'], even_length_sorted_two_page_predictions[i+1]['header']).find_longest_match()
        if(prediction_greedy_gobble.size/len(prediction['header'])>0.5):
            even_length_sorted_two_page_predictions[i+1]['count'] = even_length_sorted_two_page_predictions[i+1]['count'] + prediction['count']
            prediction['count'] = 0
    for i, prediction in enumerate(odd_length_sorted_two_page_predictions):
        if(i+1>=len(odd_length_sorted_two_page_predictions)):
            break
        prediction_greedy_gobble = SequenceMatcher(None, prediction['header'], odd_length_sorted_two_page_predictions[i+1]['header']).find_longest_match()
        if(prediction_greedy_gobble.size/len(prediction['header'])>0.5):
            odd_length_sorted_two_page_predictions[i+1]['count'] = odd_length_sorted_two_page_predictions[i+1]['count'] + prediction['count']
            prediction['count'] = 0
    even_count_sorted_two_page_predictions = sorted(even_length_sorted_two_page_predictions, key = lambda i: (i['count']), reverse=True)
    if(len(even_count_sorted_two_page_predictions)>0):
        if(even_count_sorted_two_page_predictions[0]['count'] >= (2+len(pages)//4)):
            if(debug==1): print('header', even_count_sorted_two_page_predictions[0]['header'], even_count_sorted_two_page_predictions[0]['count'])
    odd_count_sorted_two_page_predictions = sorted(even_length_sorted_two_page_predictions, key = lambda i: (i['count']), reverse=True)
    if(len(odd_count_sorted_two_page_predictions)>0):
        if(odd_count_sorted_two_page_predictions[0]['count'] >= (2+len(pages)//4)):
            if(debug==1): print('header', odd_count_sorted_two_page_predictions[0]['header'], odd_count_sorted_two_page_predictions[0]['count'])
    return {'one_page_predictions': count_sorted_one_page_predictions, 'two_page_predictions': {'even': even_count_sorted_two_page_predictions, 'odd': odd_count_sorted_two_page_predictions}}
    
######### MARK: what about processing invoices for specific charges extracted from invoices?


def predictFooter(filename, pages):
    debug = 0
    one_page_predictions = []
    two_page_predictions = []
    matching_length = 8
    if(debug==1): 
        print(len(pages), "pages in total")
    for i, page in enumerate(pages):
        if(debug==1):
            print(i, "page loop")
            print(len(page))

        footer_buffer = 500
        if(i+1==len(pages)):
            break
        if(len(page)<footer_buffer):
            footer_buffer = len(page)
            if(debug==1): print("short page", len(page))
        #if not any(prediction['count'] > 4 for prediction in predictions):
        page_length = len(page)
        next_page_length = len(pages[i+1])
        one_page_prediction = SequenceMatcher(None, pages[i], pages[i+1]).find_longest_match(page_length - footer_buffer, page_length, next_page_length - footer_buffer, next_page_length)
        if(debug==1): print(pages[i][0:200], "\n", pages[i+1][0:200])
        if(debug==1): print(one_page_prediction.size)
        if(one_page_prediction.size>matching_length):
            #string_present = pages[i].find(pages[0][prediction.a:prediction.a+prediction.size])
            one_page_predicted_footer = pages[i][one_page_prediction.a:one_page_prediction.a+one_page_prediction.size]
            if(debug==1): print(one_page_predicted_footer)
            if not any(prediction['footer'] == one_page_predicted_footer for prediction in one_page_predictions):
                one_page_predictions.append({'footer': one_page_predicted_footer, 'type': 'one-page', 'count': 1})
            else: 
                for prediction in one_page_predictions:
                    #print(prediction)
                    if((prediction['footer'] == one_page_predicted_footer) & (prediction['type']=='one-page')):
                        prediction['count'] = prediction['count'] + 1
        if(i+2==len(pages)):
            continue
        next_page_length = len(pages[i+2])
        two_page_prediction = SequenceMatcher(None, pages[i], pages[i+2]).find_longest_match(page_length - footer_buffer, page_length, next_page_length - footer_buffer, next_page_length)
        if(two_page_prediction.size>matching_length):
            two_page_predicted_footer = pages[i][two_page_prediction.a:two_page_prediction.a+two_page_prediction.size]
            #print(two_page_predicted_footer)
            if not any(prediction['footer'] == two_page_predicted_footer for prediction in two_page_predictions):
                two_page_predictions.append({'footer': two_page_predicted_footer, 'type': 'two-page', 'isEven': (i % 2==0), 'count': 1})
            else: 
                for prediction in two_page_predictions:
                    #print(prediction)
                    if((prediction['footer'] == two_page_predicted_footer) and prediction['isEven'] == (i % 2==0)):   
                        prediction['count'] = prediction['count'] + 1


    ####Sorting
    length_sorted_one_page_predictions = sorted(one_page_predictions, key = lambda i: (len(i['footer'])), reverse=True)
    if(debug==1): print(length_sorted_one_page_predictions)
    for i, prediction in enumerate(length_sorted_one_page_predictions):
        if(i+1==len(length_sorted_one_page_predictions)):
            break
        prediction_greedy_gobble = SequenceMatcher(None, prediction['footer'], length_sorted_one_page_predictions[i+1]['footer']).find_longest_match()
        if(prediction_greedy_gobble.size/len(prediction['footer'])>0.5):
            length_sorted_one_page_predictions[i+1]['count'] = length_sorted_one_page_predictions[i+1]['count'] + prediction['count']
            prediction['count'] = 0
    count_sorted_one_page_predictions = sorted(length_sorted_one_page_predictions, key = lambda i: (i['count']), reverse=True)
    if(len(count_sorted_one_page_predictions)>0):
        if(count_sorted_one_page_predictions[0]['count'] >= (2+len(pages)//4)):
            if(debug==1): print('footer', count_sorted_one_page_predictions[0]['footer'], count_sorted_one_page_predictions[0]['count'])
    length_sorted_two_page_predictions = sorted(two_page_predictions, key = lambda i: (len(i['footer'])), reverse=True)
    even_length_sorted_two_page_predictions = []
    odd_length_sorted_two_page_predictions = []
    for prediction in length_sorted_two_page_predictions:
        if prediction['isEven']==True:
            even_length_sorted_two_page_predictions.append(prediction)
        else:
            odd_length_sorted_two_page_predictions.append(prediction)
    if(debug==1): print(length_sorted_two_page_predictions)
    for i, prediction in enumerate(even_length_sorted_two_page_predictions):
        if(i+1>=len(even_length_sorted_two_page_predictions)):
            break
        prediction_greedy_gobble = SequenceMatcher(None, prediction['footer'], even_length_sorted_two_page_predictions[i+1]['footer']).find_longest_match()
        if(prediction_greedy_gobble.size/len(prediction['footer'])>0.5):
            even_length_sorted_two_page_predictions[i+1]['count'] = even_length_sorted_two_page_predictions[i+1]['count'] + prediction['count']
            prediction['count'] = 0
    for i, prediction in enumerate(odd_length_sorted_two_page_predictions):
        if(i+1>=len(odd_length_sorted_two_page_predictions)):
            break
        prediction_greedy_gobble = SequenceMatcher(None, prediction['footer'], odd_length_sorted_two_page_predictions[i+1]['footer']).find_longest_match()
        if(prediction_greedy_gobble.size/len(prediction['footer'])>0.5):
            odd_length_sorted_two_page_predictions[i+1]['count'] = odd_length_sorted_two_page_predictions[i+1]['count'] + prediction['count']
            prediction['count'] = 0
    even_count_sorted_two_page_predictions = sorted(even_length_sorted_two_page_predictions, key = lambda i: (i['count']), reverse=True)
    if(len(even_count_sorted_two_page_predictions)>0):
        if(even_count_sorted_two_page_predictions[0]['count'] >= (2+len(pages)//4)):
            if(debug==1): print('footer', even_count_sorted_two_page_predictions[0]['footer'], even_count_sorted_two_page_predictions[0]['count'])
    odd_count_sorted_two_page_predictions = sorted(odd_length_sorted_two_page_predictions, key = lambda i: (i['count']), reverse=True)
    if(len(odd_count_sorted_two_page_predictions)>0):
        if(odd_count_sorted_two_page_predictions[0]['count'] >= (2+len(pages)//4)):
            if(debug==1): print('footer', odd_count_sorted_two_page_predictions[0]['footer'], odd_count_sorted_two_page_predictions[0]['count'])
    return {'one_page_predictions': count_sorted_one_page_predictions, 'two_page_predictions': {'even': even_count_sorted_two_page_predictions, 'odd': odd_count_sorted_two_page_predictions}}


def checkHeaderForVariables(pages, predictions):
    for i, prediction in enumerate(predictions):
        if(i<3):
            for i, page in enumerate(pages):
                #print(prediction.text)
                #print(i)
                #print(prediction.text)
                #print(page.text[0:250])
                headerlocation = page.text.find(prediction.text)
                #print(headerlocation)
                #print(page.text.find('\n'))
            #print(predictions)
    return {'headerlocation': "test"}

def findPageNumbers(pages):
    pageNum = 0
    startPageNums = []
    pageNums = []

    for i, page in enumerate(pages):
        tempPageNums = re.findall(r'\d+', page.text[0:300])
        for pageNum in pageNums:
            for tempPageNum in tempPageNums:
                if(int(pageNum) == int(tempPageNum)-1):
                    if(i==1):
                        startPageNums.append(pageNum)
                    else:
                        for startPageNum in startPageNums:
                            if((int(startPageNum) + i) not in map(lambda x: int(x), tempPageNums)):
                                startPageNums.remove(startPageNum)
        pageNums = tempPageNums
    print(startPageNums)


def sizeUp(pages):
    num_pages = len(pages)
    pages_of_spans = []
    whitespace_average_pages = []
    average_summer = 0
    for i, page in enumerate(pages):
        whitespace_page_average_summer = 0
        lines = page.split('\n')
        whitespace_re = re.compile(r'[\s,\t,\r]')
        page_length = 0
        line_spans = []
        for j, line in enumerate(lines):
            num_chars = len(line)
            page_length = page_length + len(num_chars)
            whitespace_arr = whitespace_re.findall(line)
            whitespace_ratio = len(whitespace_arr)//num_chars
            whitespace_average_summer = whitespace_average_summer + whitespace_ratio
            line_spans.append({'line_number': j, 'num_chars': num_chars, 'whitespace_ratio': whitespace_ratio, 'page_number': i})
        whitespace_average = whitespace_page_average_summer//len(lines)
        whitespace_average_pages.append({'page_number': i, 'average': whitespace_average})
        pages_of_spans.append(line_spans)

    return {'num_pages': num_pages, 'average_whitespace': whitespace_average_pages}






def process(sentence):
    matcher = Matcher(nlp.vocab)
    pattern = [{"label": "HEARING", "pattern": [{"LOWER": "hearing"}]}]
    #matcher.add("hearing", [pattern])
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(pattern)
    doc=nlp(sentence)
    #print([(ent.text, ent.label_) for ent in doc.ents])
    return doc

def visualize(sentence):
    doc=nlp(sentence)
    return displacy.render(doc, style="ent")

def find_dates(sentence):
    doc = nlp(sentence)
    dates = []
    #print(doc.ents)
    for e in doc.ents:
        if(e.label_=='DATE'):
            print(e)
            dates.append(e)
    print(dates)
    return dates

def find_defined_terms(sentence):
    matcher = Matcher(nlp.vocab)
    pattern = [{"label": "DEFINED", "pattern": [{}]}]