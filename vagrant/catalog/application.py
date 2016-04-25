import json
import random
import requests
import string

from database_setup import Base, User, Category, Item
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from flask import session as user_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker


# APP SETUP =======================================================================================

app = Flask(__name__)

# Read the OAuth client ID
client_id = json.loads(open('client_secret.json', 'r').read())['web']['client_id']
app_name = 'Udacity Project 3'


# DATABASE CONNECTION =============================================================================

engine = create_engine('sqlite:///catalog.db')

# Map the database schema to the metadata of the Base class to use
# the database objects as classes when creating new objects
Base.metadata.bind = engine

# Initialize a session which acts as a staging environment for any changes to the database.
# Changes to the session are not committed to the database until database_session.commit()
database_session = sessionmaker(bind=engine)()


# HELPER FUNCTIONS ================================================================================

def createOrRetrieveUserID(user_session):
    """Create a new user and add him to the database."""

    name = user_session.get('name')
    email = user_session.get('email')

    # Try and retrieve a user with the given email or else continue to make a new user
    try:
        user = database_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        pass

    # Create a new user based on the information passed in from the session information
    user = User(name=name, email=email)

    # Add the new user to the database session and commit the change
    database_session.add(user)
    database_session.commit()

    # Retrieve the new user object as we need to return the ID
    user = database_session.query(User).filter_by(email=email).one()

    return user.id


def getUserByID(user_id):
    """Return a user given their ID."""

    user = database_session.query(User).filter_by(id=user_id).one()

    return user


def generateResponse(message, code):
    """Generate a JSON formatted response."""

    response = make_response(json.dumps(message), code)
    response.headers['Content-Type'] = 'application/json'
    return response


# ROUTE CONFIGURATION =============================================================================

@app.route('/catalog.json')
def catalogJSON():
    """Return a JSON object describing all categories and their items."""

    # Retrieve all the categories from the database
    categories = database_session.query(Category).all()

    # Create a working array so we can augment the category objects with items
    categories_collection = []

    for category in categories:
        # Serialize the given category information into a temporary element
        _ = category.serialize

        # Retrieve all the items that belong to this particular category
        items = database_session.query(Item).filter_by(category_id=category.id).all()

        # Serialize all the items and add them to the temporary element
        _['items'] = [item.serialize for item in items]

        # Add the temporary element to the working array
        categories_collection.append(_)

    # Finally, JSONify the whole working array as the final response
    return jsonify(categories=categories_collection)


@app.route('/')
@app.route('/catalog/')
def showCategories():
    """The home page. Displays all categories."""

    # Retrieve all the categories from the database
    categories = database_session.query(Category).order_by(asc(Category.name))

    # Render the homepage template containing all the categories
    return render_template('index.html',
        categories = categories,
        email = user_session.get('email')
    )


@app.route('/catalog/<category_name>/')
def showCategory(category_name):
    """The category page. Displays all the items within that category."""

    # Retrieve all the items for this category from the database
    category = database_session.query(Category).filter_by(name=category_name).one()
    items = database_session.query(Item).filter_by(category_id=category.id).all()

    # Render the category template containing all the items
    return render_template('category.html',
        items = items,
        category_name = category_name,
        email = user_session.get('email')
    )


@app.route('/catalog/<category_name>/<item_name>')
def showItem(category_name, item_name):
    """The item page. Displays all the information about a particular item."""

    # Retrieve the item from the database
    category = database_session.query(Category).filter_by(name=category_name).one()
    item = database_session.query(Item).filter_by(
        category_id = category.id).filter_by(name = item_name).one()

    # If this user is the owner, set a flag which we use to alter the template presentation
    owner = True if user_session.get('user_id') == item.user_id else False

    # Render the item template containing all the item information
    return render_template('item.html',
        item = item,
        category_name = category_name,
        owner = owner,
        email = user_session.get('email')
    )


@app.route('/catalog/add/', methods=['GET', 'POST'])
@app.route('/catalog/<category_name>/add/', methods=['GET', 'POST'])
def newItem(category_name=None):
    """The item creation page."""

    # Redirect the user to login if they are not logged in
    if 'name' not in user_session:
        return redirect('/login')

    # If we're in POST, process the form data
    if request.method == 'POST':

        post_category = request.form.get('category')
        post_name = request.form.get('name')
        post_description = request.form.get('description')

        # All fields must have a value
        if (post_category and post_name and post_description):
            # Retrieve the category that was selected for use when creating the new item
            category = database_session.query(Category).filter_by(name=post_category).one()

            # Create a new item based on the information passed in from the form data
            item = Item(
                name = post_name,
                description = post_description,
                category_id = category.id,
                user_id = user_session.get('user_id')
            )

            # Add the new item to the database session and commit the change
            database_session.add(item)
            database_session.commit()

            # Set an alert to the user that the item was added
            flash('New item successfully created: %s' % (item.name))
        # Or else we simply alert the user to try again
        else:
            flash('Please ensure all fields have a value')

        # If we were on a category page, redirect back to that
        if category_name is not None:
            return redirect(url_for('showCategory', category_name=category_name))

        # Otherwise, redirect back to the base page of all categories
        return redirect(url_for('showCategories'))
    # Else we're in GET, so present the creation form instead
    else:
        # Retrieve all the categories from the database so we can present them as form options
        categories = database_session.query(Category).order_by(asc(Category.name))

        # Pass in the category name if it exists, so we can auto-highlight the appropriate category
        return render_template('newitem.html',
            categories = categories,
            category_name = category_name,
            email = user_session.get('email')
        )


@app.route('/catalog/<category_name>/<item_name>/edit/', methods=['GET', 'POST'])
def editItem(category_name, item_name):
    """The item editing page."""

    # Redirect the user to login if they are not logged in
    if 'name' not in user_session:
        return redirect('/login')

    # Retrieve the item from the database
    category = database_session.query(Category).filter_by(name=category_name).one()
    item = database_session.query(Item).filter_by(
        category_id = category.id).filter_by(name = item_name).one()

    # Alert the user if they are not the owner, as they cannot edit items that are not theirs
    if user_session.get('user_id') != item.user_id:
        # We want to alert the user that the item is not theirs and cannot be edited
        flash('Item does not belong to you and therefore cannot be edited')

        # Return to the main category page that item came from
        return redirect(url_for('showCategory', category_name=category_name))

    # If we're in POST, process the form data
    if request.method == 'POST':

        post_category = request.form.get('category')
        post_name = request.form.get('name')
        post_description = request.form.get('description')

        # All fields must have a value
        if (post_category and post_name and post_description):
            # Update the item attributes
            item.name = post_name
            item.description = post_description
            new_category_name = post_category
            new_category = database_session.query(Category).filter_by(name=new_category_name).one()
            item.category_id = new_category.id

            # Add the update item back into the database
            database_session.add(item)
            database_session.commit()

            # Set an alert to the user that the item was edited
            flash('Item successfully edited')
        # Or else we simply alert the user to try again
        else:
            flash('Please ensure all fields have a value')

        # Return to the main category page that the item came from
        return redirect(url_for('showCategory', category_name=category_name))
    # Else we're in GET, so present the editing form instead
    else:
        # Retrieve all the categories from the database so we can present them as form options
        categories = database_session.query(Category).order_by(asc(Category.name))

        return render_template('edititem.html',
            item = item,
            categories = categories,
            category_name = category_name,
            email = user_session.get('email')
        )


@app.route('/catalog/<category_name>/<item_name>/delete/', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    """The item deletion page."""

    # Redirect the user to login if they are not logged in
    if 'name' not in user_session:
        return redirect('/login')

    # Retrieve the item from the database
    category = database_session.query(Category).filter_by(name=category_name).one()
    item = database_session.query(Item).filter_by(
        category_id = category.id).filter_by(name = item_name).one()

    # Alert the user if they are not the owner, as they cannot delete items that are not theirs
    if user_session.get('user_id') != item.user_id:
        # We want to alert the user that the item is not theirs and cannot be deleted
        flash('Item does not belong to you and therefore cannot be deleted')

        # Return to the main category page that item came from
        return redirect(url_for('showCategory', category_name=category_name))

    # If we're in POST, process the form data
    if request.method == 'POST':
        # Remove the item from the database
        database_session.delete(item)
        database_session.commit()

        # Set an alert to the user that the item was deleted
        flash('Item successfully deleted')

        # Return to the main category page that the item came from
        return redirect(url_for('showCategory', category_name=category_name))
    # Else we're in GET, so present the deletion form instead
    else:
        return render_template('deleteitem.html',
            item = item,
            category_name = category_name,
            email = user_session.get('email')
        )


@app.route('/login/')
def showLogin():
    """The login page. Displays the login options."""

    # Generate a session token to avoid CSRF and add it to the login session
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    user_session['state'] = state

    # Render the login template and pass in the CSRF token
    return render_template('login.html',
        client_id = client_id,
        state = state
    )


@app.route('/oauth', methods=['POST'])
def oauth():
    """The OAuth logic. Consumes state data and tries to generate a valid OAuth token."""

    # CSRF validation. If mis-matched, abort
    if request.args.get('state') != user_session.get('state'):
        return generateResponse('Invalid state parameter.', 401)

    # Upgrade the authorization code into a credentials object or abort on error
    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(request.data)
    except FlowExchangeError:
        return generateResponse('Failed to upgrade the authorization code.', 401)

    # Get the token information from Google
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token
    response = requests.get(url)
    result = response.json()

    # Abort if there was an error passed back within the access token info
    if result.get('error') is not None:
        return generateResponse(result.get('error'), 500)

    # Verify that the access token is used for the intended user or abort
    google_id = credentials.id_token.get('sub')
    if result.get('user_id') != google_id:
        return generateResponse('User ID for token does not match given user ID.', 401)

    # Verify that the access token is valid for this app or abort
    if result.get('issued_to') != client_id:
        return generateResponse('Client ID for token does not match app client ID.', 401)

    # Verify that the user is not already connected
    existing_access_token = user_session.get('access_token')
    existing_google_id = user_session.get('google_id')

    # If so, simply respond with a 200
    if existing_access_token is not None and google_id == existing_google_id:
        return generateResponse('Current user is already connected.', 200)

    # Save the token and Google ID to enable future user validation as done directly above
    user_session['access_token'] = access_token
    user_session['google_id'] = google_id

    # Get the user information from Google
    parameters = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', params=parameters)
    data = answer.json()

    # Store the name and email of the user in their session data
    user_session['name'] = data.get('name')
    user_session['email'] = data.get('email')

    # Get an ID for the user and store it in their session data
    user_session['user_id'] = createOrRetrieveUserID(user_session)

    # We want to alert the user that they logged in successfully, so add a message to the 'flash'
    flash('You are now logged in as %s' % user_session.get('name'))

    # Return whatever just so the AJAX call has a successful response
    return 'Success'


@app.route('/deauth/')
def deauth():
    """The De-authorize logic. Logs an active user out and removes their session information."""

    # Only deauthorize a user who is currently logged in
    access_token = user_session.get('access_token')
    if access_token is None:
        # Alert the user that they are not currently logged in
        flash('You are not logged in.')

        # Redirect to the homepage
        return redirect(url_for('showCategories'))

    # Send the deauthorization request to Google
    response = requests.get('https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token)

    # If successful (200), delete the user's session information, effectively logging them out
    if response.status_code == 200:
        del user_session['access_token']
        del user_session['email']
        del user_session['google_id']
        del user_session['name']
        del user_session['user_id']

        # Retrieve all the categories from the database
        categories = database_session.query(Category).order_by(asc(Category.name))

        # Alert the user that they logged out successfully
        flash('You are now logged out.')

        # Redirect to the homepage
        return redirect(url_for('showCategories'))
    else:
        # Alert the user that the token revocation failed
        flash('Failed to revoke token for given user.')

        # Redirect to the homepage
        return redirect(url_for('showCategories'))


if __name__ == '__main__':
    app.secret_key = 'guess_this'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
