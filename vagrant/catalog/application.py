import httplib2
import json
import random
import requests
import string

from database_setup import Base, User, Category, Item
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker


# APP SETUP =======================================================================================

app = Flask(__name__)


# DATABASE CONNECTION =============================================================================

engine = create_engine('sqlite:///catalog.db')

# Map the database schema to the metadata of the Base class so we can use
# the database objects as classes when creating new objects
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# We initialize a session which acts as a staging environment for any changes to the database.
# Changes to the session are not committed to the database until we call session.commit()
session = DBSession()


# ROUTE CONFIGURATION =============================================================================

@app.route('/catalog.json')
def catalogJSON():
    """Return a JSON object describing all categories and their items."""

    # Retrieve all the categories from the database
    categories = session.query(Category).all()

    # Create a working array so we can add items into the category objects
    categories_collection = []

    for category in categories:
        # Serialize the given category information into a temporary element
        _ = category.serialize

        # Retrieve all the items that belong to this particular category
        items = session.query(Item).filter_by(category_id=category.id).all()

        # Serialize all the items and add them to the temporary element
        _['items'] = [item.serialize for item in items]

        # Add the temporary element to the working array
        categories_collection.append(_)

    # Finally, JSONify the whole working array as the final response
    return jsonify(categories=categories_collection)


if __name__ == '__main__':
    app.secret_key = 'guess_this'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
