from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from mainPage.models import Portfolio, Background_img, Specialisation, About, Blog, Contact, People, Visit_detail


class Background_imgInline(admin.StackedInline):
    fields = ['image']
    model = Background_img
    extra = 1

class SpecialisationInline(admin.StackedInline):
    fields = ['specialisation_name']
    model = Specialisation
    max_num = 3

class PortfolioAdmin(admin.ModelAdmin):
    fields = ['title_text','name_content']
    inlines = [Background_imgInline, SpecialisationInline]
    list_display = ('name_content', 'last_updated')

class AboutAdmin(admin.ModelAdmin):
    fields = ['preview', 'image', 'content']
    list_display = ('name', 'last_updated')
    readonly_fields = ["preview"]

    def preview(self, instance):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = reverse('mainPage:serve_image', args=["ab"]),
            width=300,
            height=300,
            )
    )
    preview.short_description = "Current image preview"

class BlogAdmin(admin.ModelAdmin):
    fields = ['title', 'pub_date', 'link']
    list_display = ('title', 'pub_date', 'was_published_recently', 'last_updated',)
    list_filter = ['pub_date']

class ContactAdmin(admin.ModelAdmin):
    fields = ['types', 'link']
    list_display = ('types','last_updated', 'link')

class Visit_detailInline(admin.StackedInline):
    fields = ['user_agent', 'visit_time', 'name', 'email_id', 'message', 'city', 'region', 'country']
    model = Visit_detail
    ordering = ('-visit_time',)

    readonly_fields = ['user_agent', 'name', 'email_id', 'visit_time', 'message']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class PeopleAdmin(admin.ModelAdmin):
    fields = ['ip_address', 'no_of_visits']
    readonly_fields = ('ip_address', 'no_of_visits', 'last_visited')
    list_display = ('ip_address', 'no_of_visits', 'details','last_visited')
    inlines = [Visit_detailInline]
    search_fields = ['ip_address', 'no_of_visits', 'last_visited']
    list_filter = ['no_of_visits', 'last_visited']

    def details(self, instance):
        return format_html('<a href="https://www.infobyip.com/ip-{ip}.html" target="_blank">IP details</a>', ip=instance.ip_address)
    details.short_description = "Look up"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class Visit_detailAdmin(admin.ModelAdmin):
    list_display = ['get_people_ip', 'user_agent', 'city' ,'region' ,'country' ,'name', 'email_id', 'message', 'visit_time']
    search_fields = ['people__ip_address', 'user_agent', 'city' ,'region' ,'country' ,'name', 'email_id', 'message', 'visit_time']
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False
    
    

# Register your models here.
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(About, AboutAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(People, PeopleAdmin)
admin.site.register(Visit_detail, Visit_detailAdmin)

admin.site.site_header = "Admin"
admin.site.site_title = "Admin"
admin.site.unregister(Group)