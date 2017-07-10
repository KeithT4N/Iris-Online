from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from .models import *
from django.shortcuts import Http404
from django.http import HttpResponse
import json
from django.http import QueryDict
from IrisOnline.decorators import admin_required
from django.shortcuts import redirect
from django.contrib.auth import login, logout, authenticate


def admin_sign_out(request):
    logout(request)
    return redirect('/admin-sign-in/')


class AdministratorSignInView(View):
    @staticmethod
    def get(request):
        return render(request, 'admin_sign_in.html')

    @staticmethod
    def post(request):
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'admin_sign_in.html', {
                'error': 'Invalid Credentials'
            })
        elif not user.is_superuser:
            return render(request, 'admin_sign_in.html', {
                'error': 'Customer account entered'
            })
        else:
            login(request, user)
            return redirect('/entity-management/')


class EntityManagementView(View):
    @staticmethod
    @login_required(login_url='/admin-sign-in/')
    @admin_required
    def get(request):
        stalls = Stall.objects.all()
        return render(request, 'entity_management.html', {
            "stalls": stalls,
            "username": request.user.username
        })


class ProductView(View):
    @staticmethod
    def post(request, stall_id):

        if 'photo' not in request.FILES:
            return HttpResponse(status=400)

        dict = {
            "product_name": request.POST.get('name'),
            "description": request.POST.get('description'),
            "price": request.POST.get('price'),
            "quantity": request.POST.get('quantity')
        }

        errors = handle_errors(dict)
        print(not errors)

        if not errors:
            new_product = Product()
            new_product.name = dict["product_name"]
            new_product.description = dict["description"]
            new_product.photo = request.FILES.get('photo')
            new_product.price = dict["price"]
            new_product.stall = Stall.objects.get(pk=stall_id)
            new_product.quantity = dict["quantity"]
            new_product.save()

            data = {
                "new_product": new_product.name
            }

            return HttpResponse(
                json.dumps(data),
                content_type="application/json"
            )

        return HttpResponse(
            json.dumps(errors),
            content_type="application/json",
            status=400
        )

    @staticmethod
    def put(self, request, stall_id):
        # this function is never used
        put = QueryDict(request.body)
        dict = {
            "product_name": put.get("product_name"),
            "description": put.get('description'),
            "price": put.get('price'),
            "quantity": put.get('quantity')
        }

        print(dict)
        errors = handle_errors(dict)
        print(errors)

        if not errors:
            product = Product.objects.get(id=put.get("product_id"))
            product.name = put.get("product_name")
            product.description = put.get("description")
            product.price = put.get("price")
            product.quantity = put.get("quantity")
            if 'photo' in request.FILES:
                product.photo = request.FILES.get('photo')
            product.save()

            data = {
                "product": product.name
            }

            return HttpResponse(
                json.dumps(data),
                content_type="application/json"
            )

        return HttpResponse(
            json.dumps(errors),
            content_type="application/json",
            status=400
        )


class StallView(View):
    # noinspection PyBroadException
    @staticmethod
    def get(request, stall_id):
        try:
            stall = Stall.objects.get(id=stall_id)
            products = Product.objects.all().filter(stall=stall)
        except:
            raise Http404("Stall does not exist")

        stalls = Stall.objects.all()
        return render(request, 'entity_management.html', {
            "stalls": stalls,
            "active_stall": stall,
            "products": products,
        })

    @staticmethod
    def post(request):
        dict = json.loads(request.body)
        new_stall = Stall()
        new_stall.name = dict["stall_name"]
        new_stall.save()

        data = {
            "new_stall": new_stall.name
        }
        return HttpResponse(
            json.dumps(data),
            content_type="application/json"
        )

    @staticmethod
    def put(request, stall_id):
        dict = json.loads(request.body)
        try:
            stall = Stall.objects.get(pk=stall_id)
            print(stall)
            old_name = stall.name  # old name stored for debugging purposes (sent in JSON response)
            stall.name = dict["modified_name"]
            stall.save()

        except:
            raise Http404("Stall does not exist")
        data = {
            "old_name": old_name,
            "new_name": stall.name
        }
        return HttpResponse(
            json.dumps(data),
            content_type="application/json"
        )

    @staticmethod
    def delete(self, stall_id):

        try:
            Stall.objects.get(pk=stall_id).delete()

        except:
            raise Http404("Stall does not exist")

        data = {

        }
        return HttpResponse(
            json.dumps(data),
            content_type="application/json"
        )


def handle_errors(dict):
    errors = []
    if is_invalid(dict["product_name"]):
        errors.append("Error Missing: Name field required")
    if is_invalid(dict["price"]):
        errors.append("Error Missing: Price field required")
    if is_invalid(dict["quantity"]):
        errors.append("Error Missing: Quantity field required")
    if is_invalid(dict["description"]):
        errors.append("Error Missing: Description field required")

    return errors


def is_invalid(item):
    return item is None or item == ""


def update_product(request, stall_id):
    request_data = {
        "product_name": request.POST.get('name'),
        "description": request.POST.get('description'),
        "price": request.POST.get('price'),
        "quantity": request.POST.get('quantity')
    }

    errors = handle_errors(request_data)
    print(errors)

    if not errors:
        product = Product.objects.get(id=request.POST.get("product_id"))
        product.name = request_data["product_name"]
        product.description = request_data["description"]
        product.price = request_data["price"]
        product.quantity = request_data["quantity"]
        if 'photo' in request.FILES:
            product.photo = request.FILES.get('photo')
        product.save()

        data = {
            "product": product.name
        }

        return HttpResponse(
            json.dumps(data),
            content_type="application/json"
        )

    return HttpResponse(
        json.dumps(errors),
        content_type="application/json",
        status=400
    )
