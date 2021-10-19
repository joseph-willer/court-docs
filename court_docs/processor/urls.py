from django.urls import path

from . import views

app_name = 'processor'
urlpatterns = [
    path('', views.index, name='index'),
    path('visualize', views.visualize, name='visualizer'),
    path('dates', views.find_dates, name='date list'),
    path('pdf', views.extract_pdf, name="pdf extracter"),
    path('documents', views.document_list, name='documents'),
    path('document/<int:doc_id>/<slug:slug>', views.detail, name='document'),
    path('agencies', views.get_agencies, name='agencies'),
    path('search', views.search, name='search'),
    path('search/<str:search>', views.search_for_documents, name='search results'),
    path('<str:req_title>/usc/<str:req_section>', views.get_us_code, name='us code'),
    path('document/download/<slug:slug>', views.download_pdf, name='pdf_download')
]