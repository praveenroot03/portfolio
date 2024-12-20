from django.db import models
from django.utils import timezone
import datetime
from io import BytesIO
from PIL import Image, ExifTags
from django.core.files import File
from django.core.exceptions import ValidationError
from mainPage.utils import utlity
from django.db.models.aggregates import Count
from random import randint


def compress(image):
    im = Image.open(image)
    print(im.format)
    try:
        if im.format != 'PNG':
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation' : break 
            exif=dict(im._getexif().items())

            if exif[orientation] == 3:
                im=im.rotate(180, expand=True)
            elif exif[orientation] == 6:
                im=im.rotate(270, expand=True)
            elif exif[orientation] == 8 :
                im=im.rotate(90, expand=True)
    except:
        pass
    
    im = im.convert('RGB')
    im_io = BytesIO()     
    im.save(im_io,format='JPEG', quality=60)
    new_image = File(im_io, name=image.name)
    return new_image


class Portfolio(models.Model):
    title_text = models.CharField(max_length=50)
    name_content = models.CharField(max_length=50)
    last_updated = models.DateTimeField(default=timezone.now)


    def save(self, *args, **kwargs):
        self.last_updated = timezone.now()
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_content


class Background_img(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE )
    image = models.ImageField(upload_to='mainPage/background_img')

    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]

    def save(self, *args, **kwargs):
        new_image = compress(self.image)
        self.image = new_image
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.image).split('/')[-1]


class Specialisation(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE )
    specialisation_name = models.CharField(max_length=50)

    def __str__(self):
        return self.specialisation_name

    def save(self, *args, **kwargs):
        if self.__class__.objects.count() == 4:
            raise ValidationError("Only three specialisation allowed")
        super().save(*args, **kwargs)


class About(models.Model):
    name = models.CharField(default='about', editable= False, primary_key=True, max_length=5)
    image = models.ImageField(upload_to='mainPage/about_image')
    content = models.TextField(max_length=10000)
    last_updated = models.DateTimeField(default=timezone.now)


    def save(self, *args, **kwargs):
        self.last_updated = timezone.now()
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        new_image = compress(self.image)
        self.image = new_image
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(max_length=50)
    pub_date = models.DateTimeField('date published')
    link = models.URLField(max_length=100)
    last_updated = models.DateTimeField(default=timezone.now)

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=60) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.last_updated = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Contact(models.Model):
    TYPES = [
        ('fa-linkedin', 'Linkedin'),
        ('fa-instagram', 'Instagram'),
        ('fa-github', 'Github'),
        ('fa-twitter', 'Twitter'),
        ('fa-envelope', 'Email')
    ]
    types = models.CharField(max_length=20, choices=TYPES, primary_key=True)
    link = models.CharField(max_length=100)
    last_updated = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.last_updated = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_types_display()


class People(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    no_of_visits = models.IntegerField(default=1)
    last_visited = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.last_visited = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ip_address


class Visit_detail(models.Model):
    people = models.ForeignKey(People, on_delete=models.CASCADE)
    user_agent = models.CharField(max_length=150)
    name = models.CharField(max_length=25)
    email_id = models.EmailField()
    message = models.TextField(max_length=1000)
    visit_time = models.DateTimeField(default=timezone.now)
    city = models.CharField(max_length=25, null=True)
    region = models.CharField(max_length=25, null=True)
    country = models.CharField(max_length=5, null=True)

    def save(self, *args, **kwargs):
        location = utlity.get_location_via_ip(utlity ,self.people.ip_address)
        if location:
            self.city = location.get("city")
            self.region = location.get("region")
            self.country = location.get("country")    
        super().save(*args, **kwargs)

    def __str__(self):
        return self.people.ip_address

    def get_people_ip(self):
        return self.people.ip_address
    
    get_people_ip.admin_order_field = "people__ip_address"
    get_people_ip.short_description = "IP Address"
    

            