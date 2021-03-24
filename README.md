This is the repository for the IHS CS Club language learning app.

Instructions for running:
Make sure you are running in a virtual environment and have the dependencies installed. They may be installed with
```
$ pip install -r requirements.txt
```

Then, execute the main script:
```
$ python main.py
```

ISSUE: Single-page or multi-page? Currently the app is multi-page. This could cause difficulty if we want to port the app to a different frontend later (non-browser, such as a mobile app or desktop app), for which an almost pure REST interface will be necessary. At this early stage as of 3/24/2021 it would be very easy to convert it into a single-page application, so we should make this decision quickly!

TODO list
+ Allow login by email
+ Allow decks to be uploaded as JSON files
+ Create deck catalog and user profiles
+ Create practice tool
+ Perhaps create online deck-creation tool
+ Find a way to make deployment secure
+ Add CSS
+ Perhaps convert to a single-page application.
