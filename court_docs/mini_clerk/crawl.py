import requests
import os
import xml.etree.ElementTree as ET

from requests.api import head

base_url = "https://www.federalregister.gov/api/v1/"

def getagencies():
    endpoint = "agencies"
    response = requests.get(base_url+endpoint)
    return response

def searchdocs(search):
    endpoint = "documents.json?per_page=20&conditions[term]="+search
    response = requests.get(base_url+endpoint)
    return response

def getpdf(title, url):
    response = requests.get(url)
    write_path = '/data/pdfs/'+title+'.pdf'
    with open(write_path, 'wb') as file:
        file.write(response.content)
    return write_path
    
def getuscode(input_title, input_section):
    title_validator = []
    section_number = ''
    heading = ''
    lines = []
    number = ''

    for i in range(1, 9, 1):
        title_validator.append('0'+str(i))
    for i in range(10, 54, 1):
        title_validator.append(str(i))
    try: 
        if input_title in title_validator:
            print('title input step 1')
        else:
            if '0'+input_title in title_validator:
                input_title = '0'+input_title
                print('input title valid')
            else:
                return {'heading': "Error", 'number': -1, 'lines:': []}
                raise ValueError('that\'s not a title in the US Code')
    except ValueError:
        print('please input a real title')
    print('usc'+input_title+'.xml')
    with open('/data/us_code/usc'+input_title+'.xml', 'r') as file:
        schema = '{http://xml.house.gov/schemas/uslm/1.0}'
        tree = ET.parse(file)
        root = tree.getroot()
        sub_number = ''
        #id_root_length = len(root.find('uscDoc').attrib['identifier'].split('/')) #get the number of sections of /us/usc/txx
        #print(len(root))
        toc = root.findall(schema+'main/'+schema+'title/'+schema+'chapter/'+schema+'toc/'+schema+'layout/'+schema+'tocItem/')
        sections = root.findall(schema+'main/'+schema+'title/'+schema+'chapter/')
        
        #print(toc)
        if(len(toc)>0):
            for tocItem in toc:
              print(tocItem.tag)
        else:
            print('no tocs found')
            #print(section)
        #print(subtree)

            #print(el.attrib['identifier'])
            #print(root.find('section/content'))
        print('YFUJCIOWHFJLKSFD')
        i = 0
        for section in sections:
            print(i, section.tag)
            i+=1
            #print(len(section), section.tag)
            #print(section.keys())
            #if section.tag == schema+'num':
            #    number = section.text

            #if section.tag == schema+'heading':
                #heading = section.text

            if section.tag == schema+'section':
                ident = section.attrib['identifier'].split('/')
                
                print(''.join(ident[4:]))
                
                if ident[4] == ('s'+input_section):
                    #print('test')
                    #print(ident)
                    for subsection in section.findall('*'): 
                        #print(section.tag, subsection.tag)
                        #print(subsection)
                        temp_line = ''
                        if subsection.tag == schema+'num':
                            print('num'+subsection.text)
                            sub_number = subsection.text
                            temp_line = temp_line + sub_number
                            #print(sub_number, subsection.text)
                        if subsection.tag == schema+'heading':
                            heading = subsection.text
                            print(heading)
                            #if(heading!=None): print('----'+heading)
                        if subsection.tag == schema+'content':
                            for line in subsection.iter():
                                print('line', line.text)
                                #temp_line = temp_line + line.text
                                #print(line.tag)
                                lines.append(line.text)
                                #lines.append(line.tag)
                        if subsection.tag == schema+'subsection':
                            sub_subsections = subsection.findall('*')
                            for sub_subsection in sub_subsections:
                                if sub_subsection.tag == schema+'num':
                                    #print('\n')
                                    lines.append(sub_subsection.text)
                                    print('sub_sub_num', sub_subsection.text)
                                if sub_subsection.tag == schema+'heading':
                                    print('sub_sub_heading', sub_subsection.text)
                                    lines.append(sub_subsection.text)
                                    #print('\n') 
                                if sub_subsection.tag == schema+'chapeau':
                                    lines.append(sub_subsection.text)
                                    print('sub_sub_chapeau', sub_subsection.text)
                                if sub_subsection.tag == schema+'content':
                                        content = []
                                        for line in sub_subsection.itertext():
                                            content.append(line)
                                        print('sub_subcontent', ' '.join(content))
                                        lines.append(' '.join(content))
                                if sub_subsection.tag == schema+'paragraph':
                                    for sub_paragraph in sub_subsection.findall('*'):
                                        if sub_paragraph.tag == schema+'num':
                                            lines.append(sub_paragraph.text)
                                            print('sub_para_num', sub_paragraph.text)
                                        if sub_paragraph.tag == schema+'chapeau':
                                            print(sub_paragraph.text)
                                            lines.append(sub_paragraph.text)
                                            print('sub_para_chapeau', sub_paragraph.text)
                                        if sub_paragraph.tag == schema+'content':
                                            content = []
                                            for line in sub_paragraph.itertext():
                                                content.append(line)
                                            print('sub_para_content', ' '.join(content))
                                            lines.append(' '.join(content))
                                        if sub_paragraph.tag == schema+'subparagraph':
                                            for sub_sub_paragraph in sub_paragraph.findall('*'):

                                                if sub_sub_paragraph.tag == schema+'num':
                                                    lines.append(sub_sub_paragraph.text)
                                                    print('sub_sub_para', sub_sub_paragraph.text)

                                                if sub_sub_paragraph.tag == schema+'content':
                                                    content = []
                                                    for sub_sub_sub_paragraph in sub_sub_paragraph.itertext():
                                                        content.append(sub_sub_sub_paragraph)
                                                    print('sub_sub_para_content', ' '.join(content))
                                                    lines.append(' '.join(content))

                                                if sub_sub_paragraph.tag == schema+'chapeau':
                                                    print('sub_sub_para_chapeau', sub_sub_paragraph.text)

                                                if sub_sub_paragraph.tag == schema+'clause':
                                                    clause = sub_sub_paragraph.findall('*')
                                                    for sub_clause in clause:
                                                        if sub_clause.tag == schema+'num':
                                                            lines.append(sub_clause.text)
                                                            print('sub_clause_num', sub_clause.text)
                                                        if sub_clause.tag == schema+'content':
                                                            content = []
                                                            for line in sub_clause.itertext():
                                                                content.append(line)
                                                            print(' '.join(content))
                                                            lines.append(' '.join(content))

                                #if sub_subsection.tag == schema+'content':
                                #    for line in sub_subsection.iter():
                                #        print(line.text)
                                #        lines.append(line.text)
                                
                                
                                    

        #print(lines)
                    #paragraphs = section.findall(schema+'content/')
                    #for paragraph in paragraphs:
                    #    print(paragraph.text)
                    #    lines.append(paragraph.text)

        
        return {'heading': heading, 'number': sub_number, 'lines': lines}
