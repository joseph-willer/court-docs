from django.contrib import admin
from .models import Document, Page, PrefixSuffixPrediction, Prediction


class PageInline(admin.TabularInline):
    model = Page

class PredictionInLine:
    model = Prediction

class PrefixSuffixPredictionInLine(admin.TabularInline):
    model = PrefixSuffixPrediction
    inlines = [
        PredictionInLine
    ]


class DocumentAdmin(admin.ModelAdmin):
    inlines = [
        PageInline,
        PrefixSuffixPredictionInLine,
    ]
    exclude = ('predictions', )

# Register your models here.
admin.site.register(Document, DocumentAdmin)
admin.site.register(Page)
admin.site.register(PrefixSuffixPrediction)
admin.site.register(Prediction)

