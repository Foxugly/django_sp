python3 manage.py makemigrations
python3 manage.py makemigrations customuser
python3 manage.py makemigrations meeting
python3 manage.py makemigrations website
python3 manage.py migrate
python3 manage.py createsuperuser --username test --email 'test@test.be' --password 'renaud' --noinput
python3 manage.py runserver