import requests

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
    
    