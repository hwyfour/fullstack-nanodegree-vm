from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item


# DATABASE CONNECTION =============================================================================

engine = create_engine('sqlite:///catalog.db')

# Map the database schema to the metadata of the Base class so we can use
# the database objects as classes when creating new objects
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# We initialize a session which acts as a staging environment for any changes to the database.
# Changes to the session are not committed to the database until we call session.commit()
session = DBSession()


# USER CREATION ===================================================================================

user_1 = User(name="House Owner", email="owner@house.com")
session.add(user_1)

session.commit()


# CATEGORY CREATION ===============================================================================

category_1 = Category(name="Electronics")
session.add(category_1)

category_2 = Category(name="Furniture")
session.add(category_2)

category_3 = Category(name="Books")
session.add(category_3)

category_4 = Category(name="Clothing")
session.add(category_4)

category_5 = Category(name="Artwork")
session.add(category_5)

session.commit()


# ITEM CREATION ===================================================================================

# Electronics (category_1)
item_1 = Item(
       name="Philips Hue Lights",
       description="A home lighting system that enables you to turn your apartment into a party.",
       user_id=1,
       category=category_1
)
session.add(item_1)

# Furniture (category_2)
item_2 = Item(
       name="Couch",
       description="A comfy place to put your butt.",
       user_id=1,
       category=category_2
)
session.add(item_2)

item_3 = Item(
       name="Chair",
       description="A very hard, flat surface which is not nearly as comfy as the couch.",
       user_id=1,
       category=category_2
)
session.add(item_3)

item_4 = Item(
       name="Carpet",
       description="A soft, green, fuzzy fur carpet for cuddling on.",
       user_id=1,
       category=category_2
)
session.add(item_4)

item_5 = Item(
       name="Desk",
       description="A nice glass surface for working on.",
       user_id=1,
       category=category_2
)
session.add(item_5)

# Books (category_3)
item_6 = Item(
       name="Atlas Shrugged",
       description="An epic tome with multi-hour long speeches and 500 too many pages.",
       user_id=1,
       category=category_3
)
session.add(item_6)

item_7 = Item(
       name="The Iliad",
       description="An historic epic story with a bit of everything. If it were written post-1950, it'd even have the kitchen sink.",
       user_id=1,
       category=category_3
)
session.add(item_7)

# Clothing (category_4)
item_8 = Item(
       name="Hippie Sweater",
       description="A warm, fuzzy sweater that's perfect for nights on the patio.",
       user_id=1,
       category=category_4
)
session.add(item_8)

item_9 = Item(
       name="Angry Birds Toque",
       description="A slightly worn, but comfortable, wool helmet for those times you feel like catapulting yourself into structures.",
       user_id=1,
       category=category_4
)
session.add(item_9)

# Artwork (category_5)
item_10 = Item(
       name="Trippy Poster",
       description="A psychedelic experience that needs to be seen to be believed.",
       user_id=1,
       category=category_5
)
session.add(item_10)

item_11 = Item(
       name="Judge Dredd Poster",
       description="I. AM. THE. POSTER.",
       user_id=1,
       category=category_5
)
session.add(item_11)

session.commit()


# CLEANUP =========================================================================================

print "Database primed with data."
