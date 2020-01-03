sudo sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update
sudo apt-get install sublime-text google-chrome-stable python3-venv git libmysqlclient-dev build-essential libssl-dev libffi-dev python3-dev gcc libssl-dev apache2 php php-gettext libapache2-mod-php mysql-server phpmyadmin
pip install --upgrade pip
pip install --upgrade setuptools
pip install pymysql
sudo apt install apache2
