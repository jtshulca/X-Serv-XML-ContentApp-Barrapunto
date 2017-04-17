from django.shortcuts import render
from django.http import HttpResponse
from barra_punto.models import Pages
from django.views.decorators.csrf import csrf_exempt
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import urllib.request

# Create your views here.

contenidoRSS = ""

class myContentHandler(ContentHandler):

    def __init__(self):
        self.inItem = False
        self.inContent = False
        self.theContent = ""

    def startElement(self, name, attrs):
        if name == 'item':
            self.inItem = True
        elif self.inItem:
            if name == 'title':
                self.inContent = True
            elif name == 'link':
                self.inContent = True

    def endElement(self, name):
        if name == 'item':
            self.inItem = False
        elif self.inItem:
            if name == 'title':
                self.titulo_nuevo = self.theContent
                self.inContent = False
                self.theContent = ""
            elif name == 'link':
                global contenidoRSS
                self.html_nuevo = self.theContent
                contenidoRSS += ("<li><a href='" + self.html_nuevo + "'>" +
                             self.titulo_nuevo + "</a></li>\n")
                self.inContent = False
                self.theContent = ""

    def characters(self, chars):
        if self.inContent:
            self.theContent = self.theContent + chars

def update(request):
    global contenidoRSS
    theParser = make_parser()
    theHandler = myContentHandler()
    theParser.setContentHandler(theHandler)
    url = "http://barrapunto.com/index.rss"
    xmlFile = urllib.request.urlopen(url)
    theParser.parse(xmlFile)
    respuesta = "Los contenidos de barrapunto se han actualizado<br>"
    respuesta += "Ahora puedes ir a la página o añadir una"
    return HttpResponse(respuesta)

def show(request):
    record = Pages.objects.all()
    respuesta = "Para ver el contenido de barrapunto, actualizalo --> /update/<br>"
    respuesta += "Pages Found:"			
    for page in record:
        respuesta += "<li>/" + page.name + " --> " + page.page
    return HttpResponse(respuesta)

@csrf_exempt
def show_content(request, resource):
    if request.method == "GET":
        global contenidoRSS
        try:
            page = Pages.objects.get(name=resource)
            respuesta = "Page Found: /" + page.name + " -> "
            respuesta += page.page + "<br>"
            respuesta += "<h1>Titulares de barrapunto</h1>\n"
            respuesta += contenidoRSS
        except Pages.DoesNotExist:
            respuesta = "Page not found, add: "
            respuesta += '<form action="" method="POST">'
            respuesta += "Nombre: <input type='text' name='nombre'>"
            respuesta += "<br>Página: <input type='text' name='page'>"
            respuesta += "<input type='submit' value='Enviar'></form>"
    elif request.method == "POST":
        nombre = request.POST['nombre']
        page = request.POST['page']
        pagina = Pages(name=nombre, page=page)
        pagina.save()
        respuesta = "Saved page: /" + nombre + " --> " + page
    return HttpResponse(respuesta)
