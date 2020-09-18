from mainPage.models import People, Visit_detail
from django.db.models import F
from django.utils import timezone
import datetime


class logger:

    def __init__(self):
        self.people = People

    def add(self, ip_addr, user_agent, feedback=None):
        try:
            people = People.objects.get(ip_address=ip_addr)
        except People.DoesNotExist:
            people = None
        
        if people:
            
            if timezone.now() - datetime.timedelta(minutes=5) >= people.last_visited:
                people.no_of_visits = F('no_of_visits') + 1
                people.save()
                if feedback:
                    name = feedback.get("name")
                    email = feedback.get("email")
                    msg = feedback.get("msg")
                    details = Visit_detail(people= people, user_agent=user_agent, name=name, email_id=email, message=msg)
                    details.save()
                else:
                    details = Visit_detail(people= people, user_agent=user_agent,)
                    details.save()

            elif feedback:
                name = feedback.get("name")
                email = feedback.get("email")
                msg = feedback.get("message")
                details = Visit_detail(people= people, user_agent=user_agent, name=name, email_id=email, message=msg)
                details.save()

        else:
            new_people = People(ip_address=ip_addr)
            new_people.save()
            visit_detail = Visit_detail(people= new_people,user_agent=user_agent)
            visit_detail.save()