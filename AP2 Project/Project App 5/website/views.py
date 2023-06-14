from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
import json
from .import db
import requests
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import io
import torchvision
from flask import render_template, request
from .models import UserSettings
import threading
from datetime import datetime


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    user_settings = UserSettings.query.filter_by(user=current_user).first()
    if not user_settings:
        # If no settings have been saved, set the default calorie limit to 2000
        calorie_limit = 2000
    else:
        calorie_limit = user_settings.calorie_limit

        

    if request.method == 'POST': 
        note = request.form.get('note') 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)   
            db.session.add(new_note)  
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user, calorie_limit=str(calorie_limit))

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    note_id = note['noteId']
    note = Note.query.get(note_id)

    user_settings = UserSettings.query.filter_by(user=current_user).first()
    calorie_limit = user_settings.calorie_limit

    if note:
        if note.user_id == current_user.id:
            
            calorie_limit += note.calories # add back the calories of the deleted note to the calorie limit
            
            db.session.delete(note)
            db.session.commit()

            user_settings.calorie_limit = calorie_limit # update the calorie limit in the database
            db.session.add(user_settings)  # add the updated user_settings to the session
            db.session.commit()

            flash('Food item has been removed and calories have been added back to your calorie limit.', 'success')
        else:
            flash('You are not authorized to delete this note.', 'danger')
    else:
        flash('Note not found.', 'danger')

    return jsonify({})

#@views.route('/click-note', methods=['POST'])
#def click_note():
    #note = Note.query.get(id)





@views.route('/settings', methods=['GET', 'POST'], endpoint='settings')
@login_required
def settings():
    user_settings = UserSettings.query.filter_by(user=current_user).first()
    if request.method == 'POST':
        age = request.form['age']
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        activity_level = request.form['activity-level']
        weight_loss_goal = request.form['weight-loss-goal']
        
        if user_settings:
            # update existing user settings
            user_settings.age = age
            user_settings.gender = gender
            user_settings.height = height
            user_settings.weight = weight
            user_settings.activity_level = activity_level
            user_settings. weight_loss_goal =  weight_loss_goal
            
            
        else:
            # create new user settings
            user_settings = UserSettings(age=age, gender=gender, height=height, weight=weight, activity_level=activity_level,  weight_loss_goal= weight_loss_goal, calorie_limit=2000, user=current_user)
            db.session.add(user_settings)
        
        # update weight loss goal if provided in form
        if weight_loss_goal is not None:
            user_settings.weight_loss_goal = weight_loss_goal
        
        # Calculate BMR
        if gender == "Male":
            bmr = 88.362 + (13.397 * float(weight)) + (4.799 * float(height)) - (5.677 * float(age))
        else:
            bmr = 447.593 + (9.247 * float(weight)) + (3.098 * float(height)) - (4.330 * float(age))

        # Calculate daily calorie limit based on BMR, activity level, and weight loss goal
        if activity_level == "Sedentary":
            calorie_limit = bmr * 1.2
        elif activity_level == "Lightly Active":
            calorie_limit = bmr * 1.375
        elif activity_level == "Moderately Active":
            calorie_limit = bmr * 1.55
        elif activity_level == "Very Active":
            calorie_limit = bmr * 1.725
        else:
            calorie_limit = bmr * 1.9
            
        if weight_loss_goal == "1":
            calorie_limit -= 500
        elif weight_loss_goal == "1.5":
            calorie_limit -= 750
        
        user_settings.calorie_limit = calorie_limit
        db.session.commit()
        
        flash('Your settings have been updated!', 'success')
        return redirect(url_for('views.settings'))

    return render_template('settings.html', user=current_user, settings=user_settings)





@views.route('/food', methods=['GET', 'POST'])
@login_required
def food():

    user_settings = UserSettings.query.filter_by(user=current_user).first()
    if not user_settings:
        # If no settings have been saved, set the default calorie limit to 2000.
        calorie_limit = 2000
    else:
        calorie_limit = user_settings.calorie_limit

    if request.method == 'POST':
        api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
        food = request.form.get('food')
        # Check if image file was uploaded
        img_file = request.files.get('img')

        if not food and not img_file:
            flash('No input received!', category='error')
        elif food and img_file:
            flash('Please enter only one input!', category='error')
        else:
            if food:
                # Text input case
                query = food
            else:
                # Image input case
                img_bytes = img_file.read()
                img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                img_tensor = torchvision.transforms.functional.to_tensor(img)
                img_tensor = img_tensor.unsqueeze(0)
                extractor = AutoFeatureExtractor.from_pretrained("skylord/swin-finetuned-food101")
                model = AutoModelForImageClassification.from_pretrained("skylord/swin-finetuned-food101")
                features = extractor(images=img_tensor, return_tensors="pt")
                logits = model(**features).logits
                predicted_class_idx = logits.argmax(-1).item()
                query = model.config.id2label[predicted_class_idx]
                query = query.replace("_", " ") #Replaces underscores in predictions with spaces as this was causing issues with multi-word food items

            # Call API with the query
            response = requests.get(api_url + query, headers={'X-Api-Key': 'hF5YxQt6y7hD8xXI8Zy1Ow==rrDStINNITeMcMMT'})
            if response.status_code == requests.codes.ok:
                data = response.json()
                if 'items' in data and len(data['items']) > 0:
                    item = data['items'][0]
                    if 'calories' in item:
                        calories = item['calories']
                        flash('Food item successfully logged! Food: {} | Calories logged: {}'.format(query, calories), category='success')

                        # Determine which meal the food item belongs to based on current time
                        current_time = datetime.now().time()
                        if current_time >= datetime.strptime('06:00', '%H:%M').time() and current_time <= datetime.strptime('11:59', '%H:%M').time():
                            meal_type = 'breakfast'
                        elif current_time >= datetime.strptime('12:00', '%H:%M').time() and current_time <= datetime.strptime('17:59', '%H:%M').time():
                            meal_type = 'lunch'
                        else:
                            meal_type = 'dinner'
                        
                        # Subtract logged calories from calorie_limit
                        calorie_limit = calorie_limit - calories
                        user_settings.calorie_limit = calorie_limit
                        db.session.commit()

                        if calorie_limit <= 0:
                            flash('Warning: you are now in a calorie surplus!', category='error')

                        # Create a new note with the food name, calories, and meal type
                        note = Note(
                            user_id=current_user.id,
                            data="{}: {} calories ({})".format(query, calories, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                            meal_type=meal_type, calories=calories
                        )
                        db.session.add(note)
                        db.session.commit()
                    else:
                        flash('Calories not found for food item.', category='error')
                else:
                    flash('Food item not found in database. Please try again.', category='error')
            else:
                flash('Error occurred while logging food item. Please try again later.', category='error')
                # Display the Breakfast, Lunch & Dinner cards
    breakfast_notes = Note.query.filter_by(user_id=current_user.id, meal_type='breakfast').all()
    lunch_notes = Note.query.filter_by(user_id=current_user.id, meal_type='lunch').all()
    dinner_notes = Note.query.filter_by(user_id=current_user.id, meal_type='dinner').all()

    return render_template('food.html', breakfast_notes=breakfast_notes, lunch_notes=lunch_notes, dinner_notes=dinner_notes, user=current_user, calorie_limit=str(calorie_limit))





                                                    






