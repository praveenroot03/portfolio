"""Views for the portfolio application."""

from __future__ import annotations

from typing import Dict, Iterable, List

from django.http import FileResponse, Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from mainPage.log import VisitorLogger
from mainPage.models import About, Background_img, Blog, Contact, Portfolio
from mainPage.utils import ClientMeta, Utility


utility = Utility()
visitor_logger = VisitorLogger()


def _build_about_sections(about: About | None) -> List[str]:
    if not about or not about.content:
        return []
    return [segment.strip() for segment in about.content.splitlines() if segment.strip()]


def _get_contacts() -> Iterable[Contact]:
    return Contact.objects.order_by("types")


@never_cache
def index(request):
    client = ClientMeta(
        ip_address=utility.get_client_ip_address(request),
        user_agent=utility.get_user_agent(request),
    )

    portfolio = Portfolio.objects.first()
    specialisations = portfolio.specialisation_set.all() if portfolio else []
    about = About.objects.first()
    blogs = Blog.objects.order_by("-pub_date")
    contacts = _get_contacts()

    context: Dict[str, object] = {
        "portfolio": portfolio,
        "about": _build_about_sections(about),
        "specialisations": specialisations,
        "blogs": blogs,
        "contacts": contacts,
    }

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        feedback = {"name": name, "email": email, "message": message}
        visitor_logger.add(client.ip_address, client.user_agent, feedback=feedback)

        context["response"] = "Thanks! I'll be in touch shortly."
    else:
        visitor_logger.add(client.ip_address, client.user_agent)

    return render(request, "mainPage/index.html", context)


@never_cache
def serve_image(request, types: str):
    image_field = None

    if types == "bg":
        background = Background_img.random()
        if background:
            image_field = background.image
    elif types == "ab":
        about = About.objects.first()
        if about:
            image_field = about.image

    if not image_field:
        raise Http404

    image_file = image_field.open("rb")
    return FileResponse(image_file, content_type="image/jpeg")

