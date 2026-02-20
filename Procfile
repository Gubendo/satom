web: apt-get install libpq5 -y  && python manage.py migrate && python manage.py setup_initial_data && python manage.py collectstatic --noinput && gunicorn sutom_game.wsgi:application 
