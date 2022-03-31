# FoodPlan Service

This project automates ...
You can install and run it on your local machine or use preconfigured [Heroku app](https://dvmn-recipes.herokuapp.com/admin)
Or use [this](https://t.me/dvmn_march_11_bot) Telegram bot.


![Screenshot](Screenshot.png)

## Installation
1. Clone project
```bash
git clone https://github.com/gennadis/dvmn-recipes.git
cd dvmn_recipes
```

2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install requirements
```bash
pip install -r requirements.txt
```

4. Rename `.env.example` to `.env` and fill your secrets in it.  

5. Migrate
```bash
python manage.py migrate
```

6. Create Django superuser
```bash
python manage.py createsuperuser
```

7. Use preconfigured fixtures to populate the database
```bash
python manage.py loaddata mealtypes.json allergies.json promocodes.json ingredients.json recipes.json
```

8. ...

9. Run gunicorn web server
```bash
gunicorn dvmn_recipes.wsgi
```

10. Run telegram bot
```bash
python manage.py start_bot
```

## Usage
1. Open admin panel  
Open `Recipes` app in browser [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

2. ...

3. Start using bot by typing `/start` command
