from collections import defaultdict
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_POST
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from zenmap.forms import MainMapDetailFormSet, MainMapForm, UserLoginForm
from zenmap.models import MainMap
import random
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import MainMap

from django.shortcuts import render
from .models import MainMap

from django.shortcuts import render
from django.templatetags.static import static
from .models import MainMap

from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from io import BytesIO
import qrcode
from django.http import HttpResponse
from django.urls import reverse

def qr_home(request):
    """
    Generate a QR code that opens the Home Page automatically.
    Uses request.build_absolute_uri() so no IP/domain is hardcoded.
    """
    home_url = request.build_absolute_uri(reverse('property_list'))

    qr_img = qrcode.make(home_url)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")

def home(request):
    # Latest 8 maps for the carousel
    recent_maps = MainMap.objects.all()[:8]

    # Define categories with icons and representative images
    categories = [
        {
            "slug": MainMap.CATEGORY_APARTMENTS,
            "name": "Apartments",
            "icon_class": "fa-solid fa-building",
            "image": static("video/apartment.jpg"),
        },
        {
            "slug": MainMap.CATEGORY_RESIDENTIAL,
            "name": "Residential",
            "icon_class": "fa-solid fa-house",
            "image": static("video/residential.webp"),
        },
        {
            "slug": MainMap.CATEGORY_VILLA,
            "name": "Villa",
            "icon_class": "fa-solid fa-house-chimney",
            "image": static("video/villa.webp"),
        },
        {
            "slug": MainMap.CATEGORY_HOTELS,
            "name": "Hotels",
            "icon_class": "fa-solid fa-hotel",
            "image": static("video/hotel.webp"),
        },
        {
            "slug": MainMap.CATEGORY_OFFICES,
            "name": "Offices",
            "icon_class": "fa-solid fa-briefcase",
            "image": static("video/office.jpg"),
        },
        {
            "slug": MainMap.CATEGORY_BEACH_HOUSE,
            "name": "Beach House",
            "icon_class": "fa-solid fa-umbrella-beach",
            "image": static("video/beach.webp"),
        },
        {
            "slug": MainMap.CATEGORY_COMMERCIAL,
            "name": "Commercial",
            "icon_class": "fa-solid fa-store",
            "image": static("video/commercial.webp"),
        },
        {
            "slug": MainMap.CATEGORY_OTHER,
            "name": "Other",
            "icon_class": "fa-solid fa-layer-group",
            "image": static("video/other.webp"),
        },
    ]

    return render(
        request,
        "map/home.html",
        {
            "recent_maps": recent_maps,
            "categories": categories,
        },
    )  
 
def pricing(request):
    plans = [
        {
            "name": "Basic",
            "slug": "basic",
            "css_class": "basic",
            "price": "TZS 700,000 – 900,000",
            "badge": "Starter",
            "highlight": False,
            "description": "Ideal for first-time homeowners who need a clean, functional plan.",
            "features": [
                "1 house plan (2D floor plans)",
                "Front elevation (basic)",
                "PDF delivery via email",
                "Minor layout adjustments (1 revision)",
                "Email support",
            ],
        },
        {
            "name": "Standard",
            "slug": "standard",
            "css_class": "standard",
            "price": "TZS 1,000,000 – 3,000,000",
            "badge": "Most Popular",
            "highlight": True,
            "description": "Balanced package for families who want better visuals and customization.",
            "features": [
                "Up to 2 house plans (2D floor plans)",
                "Front & rear elevations",
                "Basic 3D external view",
                "Up to 2 revisions",
                "WhatsApp & email support",
                "Ready for engineer/contractor use",
            ],
        },
        {
            "name": "Premium",
            "slug": "premium",
            "css_class": "premium",
            "price": "TZS 3,000,000+",
            "badge": "Custom",
            "highlight": False,
            "description": "Full-service design for clients who want a tailored, signature home.",
            "features": [
                "Full custom house design",
                "Detailed 2D plans + multiple elevations",
                "3D external & basic internal views",
                "Up to 4 revisions",
                "Priority WhatsApp support & consultation",
                "Optional site visit (Dar & nearby – custom quote)",
            ],
        },
    ]
    return render(request, "map/pricing.html", {"plans": plans})

# Maps by category
def maps_by_category(request, slug):
    maps_list = MainMap.objects.filter(category=slug)
    paginator = Paginator(maps_list, 12)  # 12 per page
    page_number = request.GET.get('page')
    maps_page = paginator.get_page(page_number)

    category_name = dict(MainMap.CATEGORY_CHOICES).get(slug, "Unknown Category")

    return render(request, "map/maps_by_category.html", {
        "category_name": category_name,
        "maps_page": maps_page,
    })


def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")  # username field holds email in your form
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
    else:
        form = UserLoginForm()
    return render(request, "map/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("login")


# ---------- Dashboard ----------
@login_required
def dashboard(request):
    form = MainMapForm()
    formset = MainMapDetailFormSet(prefix="details")
    maps = MainMap.objects.order_by("-id")
    return render(request, "map/dashboard.html", {"form": form, "formset": formset, "maps": maps})


# ---------- Create ----------
@login_required
def main_map_create(request):
    if request.method == 'POST':
        form = MainMapForm(request.POST, request.FILES)
        formset = MainMapDetailFormSet(request.POST, request.FILES, prefix='details')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                main_map = form.save()
                children = formset.save(commit=False)
                for c in children:
                    c.main_map = main_map
                    c.save()
                for obj in formset.deleted_objects:
                    obj.delete()
            messages.success(request, "Map created successfully.")
            return redirect('dashboard')
        messages.error(request, "Please fix the errors below.")
    else:
        form = MainMapForm()
        formset = MainMapDetailFormSet(prefix='details')

    return render(request, 'map/main_map_form.html', {
        'mode': 'create',
        'form': form,
        'formset': formset
    })


# ---------- Edit ----------
@login_required
def main_map_edit(request, pk):
    main_map = get_object_or_404(MainMap, pk=pk)
    if request.method == 'POST':
        form = MainMapForm(request.POST, request.FILES, instance=main_map)
        formset = MainMapDetailFormSet(request.POST, request.FILES, prefix='details', instance=main_map)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                children = formset.save(commit=False)
                for c in children:
                    c.main_map = main_map
                    c.save()
                for obj in formset.deleted_objects:
                    obj.delete()
            messages.success(request, "Map updated successfully.")
            return redirect('dashboard')
        messages.error(request, "Please fix the errors below.")
    else:
        form = MainMapForm(instance=main_map)
        formset = MainMapDetailFormSet(prefix='details', instance=main_map)

    return render(request, 'map/main_map_form.html', {
        'mode': 'edit',
        'object': main_map,
        'form': form,
        'formset': formset
    })

# ---------- Delete ----------
@require_POST
@login_required
def main_map_delete(request, pk):
    m = get_object_or_404(MainMap, pk=pk)
    m.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, "Map deleted successfully.")
    return redirect('dashboard')


from django.shortcuts import render, get_object_or_404
from .models import MainMap

def map_detail(request, pk):
    """
    Public detail page for a MainMap, with its child details.
    Related maps reflect the same filter context (sqm, bedrooms, floors, bathrooms, style, price).
    """
    map_item = get_object_or_404(MainMap, pk=pk)
    details = map_item.details.all().order_by("id")

    # Start with all maps except the current one
    related_maps = MainMap.objects.exclude(id=map_item.id)

    # ----- Apply filters from query params -----
    sqm = request.GET.get("sqm")
    if sqm:
        sqm_filters = {
            "under_100": {"square_meters__lt": 100},
            "100_200": {"square_meters__gte": 100, "square_meters__lt": 200},
            "200_300": {"square_meters__gte": 200, "square_meters__lt": 300},
            "300_400": {"square_meters__gte": 300, "square_meters__lt": 400},
            "400_500": {"square_meters__gte": 400, "square_meters__lt": 500},
            "500_750": {"square_meters__gte": 500, "square_meters__lt": 750},
            "750_plus": {"square_meters__gte": 750},
        }
        related_maps = related_maps.filter(**sqm_filters.get(sqm, {}))

    bedrooms = request.GET.get("bedrooms")
    if bedrooms:
        if bedrooms == "5":
            related_maps = related_maps.filter(number_of_bedrooms__gte=5)
        else:
            related_maps = related_maps.filter(number_of_bedrooms=bedrooms)

    floors = request.GET.get("floors")
    if floors:
        if floors == "4":
            related_maps = related_maps.filter(number_of_floors__gte=4)
        else:
            related_maps = related_maps.filter(number_of_floors=floors)

    bathrooms = request.GET.get("bathrooms")
    if bathrooms:
        if bathrooms == "4":
            related_maps = related_maps.filter(number_of_bathrooms__gte=4)
        else:
            related_maps = related_maps.filter(number_of_bathrooms=bathrooms)

    style = request.GET.get("style")
    if style:
        related_maps = related_maps.filter(style__iexact=style)

    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    if price_min and price_max:
        related_maps = related_maps.filter(price__gte=price_min, price__lte=price_max)
    elif price_min:
        related_maps = related_maps.filter(price__gte=price_min)
    elif price_max:
        related_maps = related_maps.filter(price__lte=price_max)

    # Limit results
    related_maps = related_maps[:4]

    return render(request, "map/map_detail.html", {
        "map": map_item,
        "details": details,
        "related_maps": related_maps,
        "map_code": map_item.code,  # 👈 added for template clarity
    })



def search_maps(request):
    query = request.GET.get('q', '')          # keyword search
    category = request.GET.get('type', '')    # type/category filter
    beds = request.GET.get('beds', '')        # bedroom filter (1,2,...,5+)
    size = request.GET.get('size', '')        # size filter (optional)
    style = request.GET.get('style', '')      # style filter
    price_min = request.GET.get('price_min', '')  # numeric price filters
    price_max = request.GET.get('price_max', '')

    results = MainMap.objects.all()

    # Keyword search
    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(detail__icontains=query) |
            Q(category__icontains=query)
        )

    # Category/type filter
    if category:
        results = results.filter(category__iexact=category)

    # Bedroom filter
    if beds:
        if beds.endswith('+'):  # handle "5+"
            num = int(beds[:-1])
            results = results.filter(number_of_bedrooms__gte=num)
        else:
            results = results.filter(number_of_bedrooms=int(beds))

    # Size filter (optional)
    if size:
        results = results.filter(size__icontains=size)

    # Style filter
    if style:
        results = results.filter(style__icontains=style)

    # Price range filter
    if price_min:
        results = results.filter(price__gte=price_min)
    if price_max:
        results = results.filter(price__lte=price_max)

    context = {
        'query': query,
        'category': category,
        'beds': beds,
        'size': size,
        'style': style,
        'price_min': price_min,
        'price_max': price_max,
        'results': results,
    }

    return render(request, 'map/search_results.html', context)


def property_list(request):
    properties = MainMap.objects.all()

    # Pata parameters kutoka GET
    style = request.GET.get('style')
    category = request.GET.get('category')
    sqm = request.GET.get('sqm')
    floors = request.GET.get('floors')
    bedrooms = request.GET.get('bedrooms')
    bathrooms = request.GET.get('bathrooms')
    q = request.GET.get('q')
    tier = request.GET.get('tier')   # NEW: from pricing page (basic/standard/premium)

    # --- Style filter ---
    if style:
        properties = properties.filter(style__iexact=style)

    # --- Category filter ---
    if category:
        properties = properties.filter(category__iexact=category)

    # --- Area (sqm) filter ---
    if sqm:
        sqm_ranges = {
            'under_100': (0, 100),
            '100_200': (100, 200),
            '200_300': (200, 300),
            '300_400': (300, 400),
            '400_500': (400, 500),
            '500_750': (500, 750),
            '750_plus': (750, None),
        }
        if sqm in sqm_ranges:
            min_val, max_val = sqm_ranges[sqm]
            if max_val:
                properties = properties.filter(square_meters__gte=min_val,
                                               square_meters__lt=max_val)
            else:
                properties = properties.filter(square_meters__gte=min_val)

    # --- Floors filter ---
    if floors:
        try:
            floors_val = int(floors)
            if floors_val >= 4:
                properties = properties.filter(number_of_floors__gte=4)
            else:
                properties = properties.filter(number_of_floors=floors_val)
        except ValueError:
            pass

    # --- Bedrooms filter ---
    if bedrooms:
        try:
            bedrooms_val = int(bedrooms)
            if bedrooms_val >= 5:
                properties = properties.filter(number_of_bedrooms__gte=5)
            else:
                properties = properties.filter(number_of_bedrooms=bedrooms_val)
        except ValueError:
            pass

    # --- Bathrooms filter ---
    if bathrooms:
        try:
            bathrooms_val = int(bathrooms)
            if bathrooms_val >= 5:
                properties = properties.filter(number_of_bathrooms__gte=5)
            else:
                properties = properties.filter(number_of_bathrooms=bathrooms_val)
        except ValueError:
            pass

    # --- Search filter (keyword) ---
    if q:
        properties = properties.filter(
            Q(title__icontains=q) |
            Q(detail__icontains=q) |
            Q(category__icontains=q) |
            Q(custom_style__icontains=q)
        )

    # --- NEW: Price / tier filter from pricing page ---
    if tier == "basic":
        # TZS 700,000 – 900,000
        properties = properties.filter(price__gte=700000, price__lte=900000)

    elif tier == "standard":
        # TZS 1,000,000 – 3,000,000
        properties = properties.filter(price__gte=1000000, price__lte=3000000)

    elif tier == "premium":
        # TZS 3,000,000+
        properties = properties.filter(price__gte=3000000)

    context = {
        'properties': properties,
        'request': request,   # for keeping search value in input
        'active_tier': tier,  # optional: use in template to show active filter
    }

    return render(request, 'map/property_list.html', context)


def about_view(request):
    success = False
    error = False

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.page = "About"
            contact.save()  # always save to DB

            try:
                send_mail(
                    subject=f"About Page Inquiry: {contact.subject}",
                    message=f"From: {contact.name} <{contact.email}>\n\nMessage:\n{contact.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['info@zenhouse.co.tz'],
                    fail_silently=False,
                )
                success = True
            except Exception as e:
                error = False  # don't treat email failure as total error
                print("Email sending (About) error:", e)
                success = True  # still mark as success since saved in DB
        else:
            error = True
    else:
        form = ContactForm()

    return render(request, "map/about.html", {"form": form, "success": success, "error": error})


def contact_view(request):
    success = False
    error = False

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.page = "Contact"
            contact.save()  # always save to DB

            try:
                send_mail(
                    subject=f"Contact Page Inquiry: {contact.subject}",
                    message=f"From: {contact.name} <{contact.email}>\n\nMessage:\n{contact.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['info@zenhouse.co.tz'],
                    fail_silently=False,
                )
                success = True
            except Exception as e:
                error = False  # don't treat email failure as total error
                print("Email sending (Contact) error:", e)
                success = True  # still mark as success since saved in DB
        else:
            error = True
    else:
        form = ContactForm()

    return render(request, "map/contact.html", {"form": form, "success": success, "error": error})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Contact
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Contact  # Ensure Contact is imported


@login_required
def message_inbox(request):
    # 1. Get Base Querysets
    inbox_qs = Contact.objects.filter(is_processed=False).order_by('-created_at')
    processed_qs = Contact.objects.filter(is_processed=True).order_by('-created_at')

    # 2. Get Counts (for badges)
    new_count = inbox_qs.count()

    # 3. Setup Pagination for Inbox (e.g., 10 per page)
    page_inbox = request.GET.get('page', 1)
    paginator_inbox = Paginator(inbox_qs, 10) 
    try:
        inbox_messages = paginator_inbox.page(page_inbox)
    except PageNotAnInteger:
        inbox_messages = paginator_inbox.page(1)
    except EmptyPage:
        inbox_messages = paginator_inbox.page(paginator_inbox.num_pages)

    # 4. Setup Pagination for Archive (e.g., 10 per page)
    # Note: We use a different URL parameter 'archive_page'
    page_archive = request.GET.get('archive_page', 1)
    paginator_archive = Paginator(processed_qs, 10)
    try:
        processed_messages = paginator_archive.page(page_archive)
    except PageNotAnInteger:
        processed_messages = paginator_archive.page(1)
    except EmptyPage:
        processed_messages = paginator_archive.page(paginator_archive.num_pages)

    context = {
        'inbox_messages': inbox_messages,
        'processed_messages': processed_messages,
        'new_count': new_count
    }
    return render(request, 'map/dashboard_messages.html', context)

# (Keep your mark_message_processed and delete_message views as they were)

@login_required
def mark_message_processed(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.is_processed = True
    contact.save()
    messages.success(request, "Message moved to Processed archive.")
    return redirect('message_inbox')

@login_required
def delete_message(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    messages.success(request, "Message deleted permanently.")
    return redirect('message_inbox')

@login_required
@require_POST
def send_reply_email(request):
    try:
        # 1. Parse the JSON data sent from the template
        data = json.loads(request.body)
        message_id = data.get('id')
        reply_body = data.get('message')
        
        # 2. Get the original message object
        contact = get_object_or_404(Contact, id=message_id)
        
        # 3. Construct the email subject
        subject = f"Re: {contact.subject} - ZenHouse Support"
        
        # 4. Send the email
        # Note: Make sure EMAIL_BACKEND and DEFAULT_FROM_EMAIL are set in settings.py
        send_mail(
            subject=subject,
            message=reply_body,
            from_email=settings.DEFAULT_FROM_EMAIL, 
            recipient_list=[contact.email],
            fail_silently=False,
        )
        
        # 5. Automatically mark the message as "Processed"
        contact.is_processed = True
        contact.save()
        
        return JsonResponse({'success': True, 'message': 'Reply sent successfully!'})
        
    except Exception as e:
        # Return error to the frontend if something goes wrong
        return JsonResponse({'success': False, 'message': str(e)}, status=500)