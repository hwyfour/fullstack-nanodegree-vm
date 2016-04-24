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
       name="Macbook Pro",
       description="A shiny, fantastic little machine for computing all the things.",
       user_id=1,
       category=category_1
)
session.add(item_1)

item_2 = Item(
       name="Philips Hue Lights",
       description="A home lighting system that enables you to turn your apartment into a party.",
       user_id=1,
       category=category_1
)
session.add(item_2)

session.commit()


# CLEANUP =========================================================================================

print "Database primed with data."
