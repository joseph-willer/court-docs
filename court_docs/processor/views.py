from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from django.http import HttpResponse, HttpResponseNotFound
from mini_clerk import extract_info as ei
from mini_clerk import crawl
import os


from .models import Document, Page, Prediction, PrefixSuffixPrediction
# Create your views here.

def index(request):
    input_data = "YOU ARE HEREBY NOTIFIED that, a Special Set hearing on the above cause is scheduled for 9:00 AM on 07-07-2021 in Room 416 at the Miami-Dade County Courthouse, 73 West Flagler Street, Miami Florida 33130. CERTIFICATE OF SERVICE \n A true and correct copy of the above notice was delivered to the parties below on 07-02-2021. If you are a person with a disability who needs any accommodation in order to participate in this proceeding, you are entitled, at no cost to you, to the provision of certain assistance. Please contact Aliean Simpkins, the Eleventh Judicial Circuit Court’s ADA Coordinator, Lawson E. Thomas Courthouse Center, 175 NW 1st Ave., Suite 2400, Miami, FL 33128, Telephone (305) 349-7175; TDD (305) 349-7174, Fax (305) 349-7355, Email: ADA@jud11.flcourts.org at least seven (7) days before your scheduled court appearance, or immediately upon receiving this notification if the time before the scheduled appearance is less than seven (7) days; if you are hearing or voice impaired, call 711."
    response = ei.process(input_data)
    for token in response:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
                token.shape_, token.is_alpha, token.is_stop)
    context = {
        'document': response
    }
    return render(request, 'processor/index.html', context)

def visualize(request):
    input_data = "YOU ARE HEREBY NOTIFIED that, a Special Set hearing on the above cause is scheduled for 9:00 AM on 07-07-2021 in Room 416 at the Miami-Dade County Courthouse, 73 West Flagler Street, Miami Florida 33130. \n CERTIFICATE OF SERVICE \n A true and correct copy of the above notice was delivered to the parties below on 07-02-2021. If you are a person with a disability who needs any accommodation in order to participate in this proceeding, you are entitled, at no cost to you, to the provision of certain assistance. Please contact Aliean Simpkins, the Eleventh Judicial Circuit Court’s ADA Coordinator, Lawson E. Thomas Courthouse Center, 175 NW 1st Ave., Suite 2400, Miami, FL 33128, Telephone (305) 349-7175; TDD (305) 349-7174, Fax (305) 349-7355, Email: ADA@jud11.flcourts.org at least seven (7) days before your scheduled court appearance, or immediately upon receiving this notification if the time before the scheduled appearance is less than seven (7) days; if you are hearing or voice impaired, call 711."
    response = ei.visualize(input_data)
    context = {
        'visualizer': response
    }
    return render(request, 'processor/visualize.html', context)

def find_dates(request):
    input_data = "YOU ARE HEREBY NOTIFIED that, a Special Set hearing on the above cause is scheduled for 9:00 AM on 07-07-2021 in Room 416 at the Miami-Dade County Courthouse, 73 West Flagler Street, Miami Florida 33130. \n CERTIFICATE OF SERVICE \n A true and correct copy of the above notice was delivered to the parties below on 07-02-2021. If you are a person with a disability who needs any accommodation in order to participate in this proceeding, you are entitled, at no cost to you, to the provision of certain assistance. Please contact Aliean Simpkins, the Eleventh Judicial Circuit Court’s ADA Coordinator, Lawson E. Thomas Courthouse Center, 175 NW 1st Ave., Suite 2400, Miami, FL 33128, Telephone (305) 349-7175; TDD (305) 349-7174, Fax (305) 349-7355, Email: ADA@jud11.flcourts.org at least seven (7) days before your scheduled court appearance, or immediately upon receiving this notification if the time before the scheduled appearance is less than seven (7) days; if you are hearing or voice impaired, call 711."
    response = ei.find_dates(input_data)
    context = {
        'dates': response
    }
    return render(request, 'processor/date_list.html', context)

def detail(request, doc_id, slug):
    doc = get_object_or_404(Document, pk=doc_id)
    pages = Page.objects.filter(document_id=doc_id)
    predictions = Prediction.objects.filter(prefixsuffixprediction__document_id=doc_id)
    ei.checkHeaderForVariables(pages, predictions)
    for page in pages:
        ei.strip_whitespace(page.text)
    #ei.findPageNumbers(pages)
    return render(request, 'processor/detail.html', {'doc': doc})

def document_list(request):
    documents = Document.objects.all()[0:20]
    return render(request, 'processor/list.html', {'documents': documents})

def get_agencies(request):
    response = crawl.getagencies()
    agencies = response.json()
    print(agencies[0]['json_url'])
    return render(request, 'processor/agencies.html', {'agencies': agencies})

def search(request):
    recent_searches = ["test", "banana", "foo", "baz", "bar"]
    return render(request, 'processor/search.html', {'recent_searches': recent_searches})


def search_for_documents(request, search):
    response = crawl.searchdocs(search)

    results = response.json()
    for result in results['results']:
        slug = slugify(result['title'][0:200])
        title = result['title']
        result['slug'] = slug
        if not Document.objects.filter(slug=slug).exists():
            pdf = crawl.getpdf(slug, result['pdf_url'])
            response = ei.extractpdf(pdf)
            save_doc(title, slug, response)
        document = Document.objects.filter(slug=slug)
        result['id'] = document[0].id
    #print(results['results'])
    return render(request, 'processor/search_results.html', {'results': results, 'search_query': search})

def download_pdf(request, slug):
    file_path = os.path.join('/data/pdfs/', slug+'.pdf')    
    if os.path.exists(file_path):    
        with open(file_path, 'rb') as fh:    
            response = HttpResponse(fh.read(), content_type="application/pdf")    
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)    
            return response


def save_doc(title, slug, response):
    pages = []
    #response = ei.extractpdf('test.pdf')
    #response = ei.extractpdf(request)
    pages = response['pages']
    start_page_num = response['start_page_num']
    doc = Document(num_pages=len(pages), title=title, slug=slug)
    doc.save()
    #print(response['predictions']['header_predictions']['one_page_predictions'][0]['header'])
    header_predictions = PrefixSuffixPrediction(document=doc, type="header")
    header_predictions.save()
    footer_predictions = PrefixSuffixPrediction(document=doc, type="footer")
    footer_predictions.save()
    
    #print(response['predictions']['header_predictions']['one_page_predictions'])

    print(response['predictions']['header_predictions']['one_page_predictions'])

    for header_prediction in response['predictions']['header_predictions']['one_page_predictions']:
        print(header_prediction['count'])
        if header_prediction['count']>0:
            predi = Prediction(text = header_prediction['header'], score=header_prediction['count'])
            predi.save()
            header_predictions.predictions.add(predi)
    header_predictions.save() ###!Performance
    
    for footer_prediction in response['predictions']['footer_predictions']['one_page_predictions']:
        print(footer_prediction)
        if footer_prediction['count']>0:
            print(footer_prediction['count'])
            predi = Prediction(text = footer_prediction['footer'], score=footer_prediction['count'])
            predi.save()
            footer_predictions.predictions.add(predi)
    footer_predictions.save() ###!Performance
    doc.save()
    for i, page in enumerate(pages):
        ei.find_dates(page)
        doc.page_set.create(page_number=i+int(start_page_num), text=page)
    doc.save()

    return True

def get_us_code(request, req_title, req_section):
    section = crawl.getuscode(req_title, req_section)
    if(len(section['lines'])>0):
        return render(request, 'processor/us-code-section.html', {'title': req_title, 'section': section})
    else:
        return HttpResponseNotFound('whoops')

def extract_pdf(request):
    pages = []
    #response = ei.extractpdf('test.pdf')
    response = ei.extractpdf(request)
    pages = response['pages']
    doc = Document(num_pages=len(pages))
    doc.save()
    print(response['predictions']['header_predictions']['one_page_predictions'][0]['header'])
    header_predictions = PrefixSuffixPrediction(document=doc, type="header")
    header_predictions.save()
    footer_predictions = PrefixSuffixPrediction(document=doc, type="footer")
    footer_predictions.save()
    
    #print(response['predictions']['header_predictions']['one_page_predictions'])

    print(response['predictions']['header_predictions']['one_page_predictions'])

    for header_prediction in response['predictions']['header_predictions']['one_page_predictions']:
        print(header_prediction['count'])
        if header_prediction['count']>0:
            predi = Prediction(text = header_prediction['header'], score=header_prediction['count'])
            predi.save()
            header_predictions.predictions.add(predi)
    header_predictions.save() ###!Performance
    
    for footer_prediction in response['predictions']['footer_predictions']['one_page_predictions']:
        print(footer_prediction)
        if footer_prediction['count']>0:
            print(footer_prediction['count'])
            predi = Prediction(text = footer_prediction['footer'], score=footer_prediction['count'])
            predi.save()
            footer_predictions.predictions.add(predi)
    footer_predictions.save() ###!Performance
    
    doc.save()
    for i, page in enumerate(pages):
        doc.page_set.create(page_number=i, text=page)
    
    doc.save()


    context = {
        'pages': pages,
        'header_predictions': response['predictions']['header_predictions']['one_page_predictions'],
        'footer_predictions': response['predictions']['footer_predictions']['one_page_predictions']
    }
    return render(request, 'processor/pdf_data.html', context)


