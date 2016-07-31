# Draw Stat #

Scrum Master Tool.

### Tools ###

* Jira API ([documentation](http://jira-python.readthedocs.org/en/latest/))
* Google calendar API ([documentation](https://developers.google.com/google-apps/calendar/v2/developers_guide_python))
* Tipboard ([documentation](http://tipboard.readthedocs.org/en/latest/index.html))


### How to get started ###

```
#!shell

cd drawstat

virtualenv venv
source venv/bin/activate

pip install -r requirements/dev.txt
```


run tipboard 

```
#!python

tipboard runserver 2222

```
http://tipboard.readthedocs.org/en/latest/configuration.html


run main script

```
#!python

python main.py
```