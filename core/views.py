from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.mail import EmailMessage 
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


def home(request):
    user = request.user if request.user.is_authenticated else None
    context = {
        'user': user,
    }
    return render(request, 'landing.html', context)
def foodintake(request):
    # user = request.user if request.user.is_authenticated else None
    # context = {
    #     'user': user,
    # }
    return render(request, 'foodintake.html')

def register(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('f_name')
        last_name = request.POST.get('l_name')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        # Check if username or email already exists
        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')
        elif pass1 != pass2:
            messages.error(request, "Your password and confirm password are not the same!")
            return redirect('register')

        # Validate password strength
        try:
            validate_password(pass1)  # This will raise a ValidationError if the password is weak
        except ValidationError as e:
            # Add error messages for weak password
            for error in e:
                messages.error(request, error)
            return redirect('register')

        # Create new user
        my_user = User(username=uname, email=email, first_name=first_name, last_name=last_name)
        my_user.set_password(pass1)  # Use set_password() to properly hash the password
        my_user.save()
        messages.success(request, "Your account has been created successfully!")
        return redirect('login')
    else:
        return render(request, 'signup.html')

        

# Login view
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass')
        # Authenticate user
        user = authenticate(request, username=username, password=password)

        # Check if user exists
        if user is None:
            messages.error(request, "Invalid UserName or Password.")
        else:
            # User exists, check password
            if user.check_password(password):
                # Password is correct, log in user
                auth.login(request, user)
                return redirect('home')
            else:
                # Incorrect password
                messages.error(request, "Invalid UserName or Password.")


    return render(request, 'login.html')

# Logout view
def logout(request):
    auth.logout(request)
    return redirect('home')





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import DailyMeal
from .forms import DailyMealForm

@login_required(login_url='login')
def meal_list(request):
    meals = DailyMeal.objects.filter(user=request.user)
    return render(request, 'meal_list.html', {'meals': meals})

@login_required(login_url='login')
def meal_detail(request, pk):
    meal = get_object_or_404(DailyMeal, pk=pk, user=request.user)
    return render(request, 'meal_detail.html', {'meal': meal})



from langchain_google_genai import ChatGoogleGenerativeAI
from .models import DailyMeal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import timedelta, datetime
from django.utils.timezone import now
# AIzaSyC6zsCK-iI-IHH0lH_zgIAfIfkF4TNhjhs
GOOGLE_API_KEY = 'AIzaSyDkS1WQkQaqgUOA-NoY2YbRbEX4c16_Ads'
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)

from IPython.display import display
from IPython.display import Markdown
import textwrap


import markdown2

def to_markdown(text):
    """Convert markdown-style text to HTML."""
    # Replace bullet points and other formatting if necessary
    text = text.replace('•', '*')  # Replace bullets if needed
    # Convert to HTML
    return markdown2.markdown(text)

@login_required(login_url='login')
@login_required
def log_meal(request):
    if request.method == 'POST':
        morning_meal = request.POST.get('morning_meal')
        morning_quantity = request.POST.get('morning_quantity')
        evening_meal = request.POST.get('evening_meal')
        evening_quantity = request.POST.get('evening_quantity')
        dinner_meal = request.POST.get('dinner_meal')
        dinner_quantity = request.POST.get('dinner_quantity')

        # Enforce 18-hour restriction
        last_entry = DailyMeal.objects.filter(user=request.user).order_by('-timestamp').first()
        if last_entry and (now() - last_entry.timestamp) < timedelta(hours=18):
            return render(request, 'wait_time.html', {'error': "You can only log a meal after 18 hours."})

        # Build prompt for AI summary
        prompt = (
            f"Generate a brief health summary based on the user's meals:\n"
            f"Morning meal: {morning_meal} ({morning_quantity})\n"
            f"Evening meal: {evening_meal} ({evening_quantity})\n"
            f"Dinner meal: {dinner_meal} ({dinner_quantity})\n"
            
            f"calculate the calories consumed by each food item in almost 2 lines\n"
            f"give heath tips to get more benifits in atmost 50 words\n"
            f"give activities to perform so that the user can maintain health in at most 50 words\n"
            f"provide healthy food suggesations to live a healthy life in at most 50 words\n"
            f"Make it friendly and concise. in at most 50 words\n")
        

        try:
            result = llm.invoke(prompt)
            summary =to_markdown(result.content)
        except Exception as e:
            summary = f"Error generating summary: {str(e)}"

        # Save meal log
        DailyMeal.objects.create(
            user=request.user,
            morning_meal=morning_meal,
            morning_quantity=morning_quantity,
            evening_meal=evening_meal,
            evening_quantity=evening_quantity,
            dinner_meal=dinner_meal,
            dinner_quantity=dinner_quantity,
            summary=summary
        )

        return redirect('meal_list')  # Redirect to your list view

    return render(request, 'log_meal.html')


from django.shortcuts import render
from langchain_google_genai import ChatGoogleGenerativeAI
import markdown2

llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)

def bmi_calculator(request):
    bmi = None
    tips = ""
    status = ""
    
    if request.method == "POST":
        try:
            height = float(request.POST.get("height")) / 100  # convert cm to meters
            weight = float(request.POST.get("weight"))
            bmi = round(weight / (height * height), 2)

            if bmi < 18.5:
                status = "Underweight"
            elif 18.5 <= bmi < 24.9:
                status = "Normal weight"
            elif 25 <= bmi < 29.9:
                status = "Overweight"
            else:
                status = "Obese"

            prompt = f"My BMI is {bmi} which is considered {status}. Give me tips to maintain or reach a healthy BMI in atmost 50 words."
            result = llm.invoke(prompt)
            tips = markdown2.markdown(result.content)

        except Exception as e:
            tips = f"<p class='text-red-500'>Error generating tips: {str(e)}</p>"

    return render(request, "bmi_calculator.html", {
        "bmi": bmi,
        "status": status,
        "tips": tips
    })
