from django.http import JsonResponse
from django.contrib.auth import get_user_model, authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

User = get_user_model()

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            return JsonResponse({'id': user.id, 'username': user.username}, status=201)  # User created
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
def signin_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(username=data['username'], password=data['password'])
        if user is not None:
            login(request, user)
            return JsonResponse({'id': user.id, 'username': user.username}, status=200)  # User logged in
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

# @csrf_exempt
# def logged_in_view(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         user = authenticate(caloriesConsumed=data['caloriesConsumed'])
#         if user is not None:
#             #TODO not sure which function to call to send post request
#             return JsonResponse({'caloriesConsumed': user.caloriesConsumed}, status=200)  # User entered num calories
#         else:
#             return JsonResponse({'error': 'Invalid input'}, status=400)
#     else:
#         return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
@csrf_exempt
@login_required
def logged_in_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            calories_consumed = data.get('caloriesConsumed')
            return JsonResponse({'caloriesConsumed': calories_consumed}, status=200)
        except KeyError:
            return JsonResponse({'error': 'Missing caloriesConsumed in request'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
@login_required
def user_info_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            
            # Update user info based on the provided data
            if 'target_weight' in data:
                user.target_weight = data['target_weight']
            if 'current_weight' in data:
                user.current_weight = data['current_weight']
            if 'height' in data:
                user.height = data['height']
            if 'weekly_physical_activity' in data:
                user.weekly_physical_activity = data['weekly_physical_activity']
            if 'gender' in data:
                user.gender = data['gender']
            if 'dietary_restriction' in data:
                # Assuming dietary_restriction is stored as an ID or name
                # You need to adjust this part based on how you manage dietary restrictions
                dietary_restriction = DietaryRestriction.objects.get(id=data['dietary_restriction'])
                user.dietary_restriction = dietary_restriction
            
            user.save()
            return JsonResponse({'message': 'User info updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    elif request.method == 'GET':
        user = request.user
        user_info = {
            'target_weight': user.target_weight,
            'current_weight': user.current_weight,
            'height': user.height,
            'weekly_physical_activity': user.weekly_physical_activity,
            'gender': user.gender,
            'dietary_restriction': user.dietary_restriction.id if user.dietary_restriction else None
        }
        return JsonResponse(user_info, status=200)
    else:
        return JsonResponse({'error': 'Only POST and GET requests are allowed'}, status=405)
    
@csrf_exempt
@login_required
def add_ingredients_to_fridge_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ingredient_names = data.get('ingredients', '').split(',')

            fridge, created = Fridge.objects.get_or_create(user=request.user)
            for ingredient_name in ingredient_names:
                ingredient_name = ingredient_name.strip()  # Remove any leading/trailing whitespace
                if ingredient_name:  # Check if the ingredient name is not empty
                    ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
                    fridge.ingredients.add(ingredient)
            fridge.save()

            return JsonResponse({'message': 'Ingredients added to fridge successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)