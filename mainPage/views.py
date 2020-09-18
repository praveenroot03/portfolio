from django.shortcuts import render
from django.http import HttpResponse
from mainPage.log import logger
from mainPage.utils import utlity
from mainPage.models import Background_img, About, Portfolio, Blog, Contact
import base64
from django.http import Http404
from django.views.decorators.cache import never_cache


@never_cache
def index(request):
    u = utlity()
    client_ip_addr = u.get_client_ip_address(request)
    client_user_agent = u.get_user_agent(request)
    logger.add(logger, client_ip_addr, client_user_agent)
    try:
        portfolio = Portfolio.objects.first()
        specialisation = portfolio.specialisation_set.all()
        about_unformated = About.objects.first().content
        about = about_unformated.split('\n')
        blogs = Blog.objects.all()
        contacts = Contact.objects.all()
        data = {'portfolio' : portfolio, 'about': about, 'specialisations' : specialisation, "blogs" : blogs, 'contacts': contacts }
    except:

        data = {'response': "Internal Server Error"}
    

    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        feedback = {"name": name, "email": email, "message": message}
        logger.add(logger, client_ip_addr, client_user_agent, feedback=feedback)

        response = "Thanks I will consider you response"
        data = {'portfolio' : portfolio, 'about': about, 'specialisations' : specialisation, "blogs" : blogs, 'contacts': contacts , 'response': response}

    return render(request, 'mainPage/index.html', data)


#here comes shitty bug, need to resolve image path
@never_cache
def serve_image(request, types):
    image_data = None
    if types and (types == "bg" or types == "ab"):
        if types == "bg":

            try:
                random_background = Background_img.random(Background_img.objects.all())
                image_data = open(random_background.image.path, "rb").read()
            except:
                raise Http404
                
        elif types == "ab":
            
            try:
                about_image = About.objects.all().first()
                image_data = open(about_image.image.path, "rb").read()
            except:
                raise Http404
    if not image_data:
        raise Http404

    return HttpResponse(image_data, content_type="image/jpeg")