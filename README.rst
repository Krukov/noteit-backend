======================================
noteit  - coming soon! - it is just prototype
======================================

.. image:: https://travis-ci.org/Krukov/noteit.svg?branch=master
    :target: https://travis-ci.org/Krukov/noteit
.. image:: https://img.shields.io/coveralls/Krukov/noteit.svg
    :target: https://coveralls.io/r/Krukov/noteit

--------------------------------
Tool for simple store some notes
--------------------------------

That The tool I created for my own purposes, but I will glad if you will use it too.

I love commandline tools like `howdoi <https://github.com/gleitz/howdoi>`_ or `fuckit <https://github.com/ajalt/fuckitpy>`_, they are really awesome.
Sometimes we want to note something simple, some usefull: command like *tar zxvf* (Really, I hate this command) or password from some service, and that it will be great, if you can make this note simple and fast, and than get this note anywhere. So, take this tool and enjoy!


How to
=================

Install
-----------------


Thare are 3 ways to use this tool:

* simple/pythonic way:

::

	pip install noteit

* manual install way 

::

	$ wget https://raw.githubusercontent.com/Krukov/noteit/master/client/noteit.py -O /usr/bin/noteit --no-check-certificate
	$ chmod +x /usr/bin/noteit



* curl way!

::

	$ python -c "$(curl -s https://raw.githubusercontent.com/Krukov/noteit/master/client/noteit.py)" [ARGUMENTS]


or 

go read CURL_MAN.md


Use
------------

::

	$ /# noteit 
	> >Input username: krukov
	> >Input your password: 
	> >If you are not registered yet, answer the question 'Do you like this tool?': yes
	> >You haven't notes
	$ /# noteit My first note
	> >Note saved
	$ /# echo "Noteit can get note from pipe" | noteit 
	>  >Note saved
	$ /# noteit 
	> >1: Noteit can get note from pipe
	> >2: My first note
