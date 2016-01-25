# Project Two

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

    	$ cd /vagrant/tournament

7. Set up the database

    	$ psql
        vagrant => create database tournament;
        vagrant => \c tournament;

8. Set up the models for the project by importing the SQL schema

        vagrant => \i tournament.sql

9. Exit from the PSQL interpreter

        vagrant => \q

10. Run the included tests file to verify the project code

    	$ python tournament_test.py

11. Celebrate!