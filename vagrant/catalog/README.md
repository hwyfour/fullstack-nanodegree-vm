# Project Three

## How to run

1. Install [Vagrant](http://vagrantup.com/) and [Virtualbox](https://www.virtualbox.org/)
2. Clone [my GitHub repository](https://github.com/hwyfour/fullstack-nanodegree-vm) containing the project code
3. Enter the repo to the main Vagrant directory

        $ cd fullstack-nanodegree-vm/vagrant

4. Set up the Vagrant box that includes the necessary environment and applications

        $ vagrant up

5. SSH into the newly created Vagrant box

        $ vagrant ssh

6. Navigate to the folder in the Vagrant box containing the project code

        $ cd /vagrant/catalog

7. Set up the database

        $ python database_setup.py

8. Prime the database with some basic information

        $ python feedme.py

9. Run the app

        $ python application.py

10. Open your browser to

        http://localhost:8000

11. Enjoy!
