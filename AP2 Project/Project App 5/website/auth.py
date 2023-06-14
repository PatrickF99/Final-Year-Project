from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, UserSettings
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in Successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email address does not exist.', category='error')    

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        age = int(request.form.get('age'))
        gender = request.form.get('gender')
        height = float(request.form.get('height'))
        weight = float(request.form.get('weight'))
        activity_level = request.form.get('activity-level')
        weight_loss_goal = request.form.get('weight-loss-goal')
        
        #if weight_loss_goal is None:
           # weight_loss_goal = 1.0  # default to 1 lb per week

        user = User.query.filter_by(email=email).first()
        if user:
            flash('This email address already exists.', category='error')
        elif len(email) < 4:
            flash('Invalid Email Address. It must exceed 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('Invalid First Name. It must exceed 1 character.', category='error')
        elif password1 != password2:
            flash('Invalid Password. Entered passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Invalid Password. It must be at least 8 characters.', category='error')
        elif age == '':
            flash('Please enter your age.', category='error')
        elif not isinstance(int(age), (int, float)):
            flash('Invalid age. Age must be a number.', category='error')
        elif int(age) < 18:
            flash('You must be at least 18 years old to use this application', category='error')
        elif height == '':
            flash('Please enter your height.', category='error')
        elif not isinstance(float(height), (int, float)):
            flash('Invalid height. Height must be a number.', category='error')
        elif weight == '':
            flash('Please enter your weight.', category='error')
        elif not isinstance(float(weight), (int, float)):
            flash('Invalid weight. Weight must be a number.', category='error')
        else:
            # add the new user to the database of users
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, 'sha256'))
            db.session.add(new_user)
            db.session.commit()

            # calculate daily calorie limit based on user input
            if gender == "Male":
                bmr = 88.362 + (13.397 * float(weight)) + (4.799 * float(height)) - (5.677 * float(age))
            else:
                bmr = 447.593 + (9.247 * float(weight)) + (3.098 * float(height)) - (4.330 * float(age))

            if activity_level == "Sedentary":
                daily_calorie_limit = bmr * 1.2
            elif activity_level == "Lightly Active":
                daily_calorie_limit = bmr * 1.375
            elif activity_level == "Moderately Active":
                daily_calorie_limit = bmr * 1.55
            else:
                daily_calorie_limit = bmr * 1.725
                
            if weight_loss_goal == "1":
                daily_calorie_limit -= 500
            elif weight_loss_goal == "1.5":
                daily_calorie_limit -= 750

            # add the user settings to the database
            new_user_settings = UserSettings(age=age, gender=gender, height=height, weight=weight, activity_level=activity_level, weight_loss_goal=weight_loss_goal, calorie_limit=daily_calorie_limit, user=new_user)
            db.session.add(new_user_settings)
            db.session.commit()

            # update the weight loss goal in the user settings object
            new_user_settings.weight_loss_goal = weight_loss_goal
            db.session.commit()

            login_user(new_user, remember=True)
            flash('Account Created! Welcome, ' + first_name + '!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)





#auth.route('/food', methods=['GET','POST'])
#def foodapi():
 #   if request.method == 'POST':
  #      api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
   #     food = request.form.get('food')
    #    print("Food entered:", food)
     #   query = food
      #  response = requests.get(api_url + query, headers={'X-Api-Key': 'hF5YxQt6y7hD8xXI8Zy1Ow==rrDStINNITeMcMMT'})
       # if response.status_code == requests.codes.ok:
        #    print(response.text)
        #else:
         #   flash('Invalid Response Status', category='error')
        
    

