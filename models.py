from database import Base
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum, DateTime, PrimaryKeyConstraint, Text, DECIMAL
import enum


class UserRole(enum.Enum):
    admin = "admin"
    user = "user"


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    firstName = Column(String(255))
    lastName = Column(String(255))
    bio = Column(String(500))
    profilePhoto = Column(String(255), default=None)
    dateOfBirth = Column(DateTime)
    phoneNumber = Column(String(30))
    password = Column(String(300), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    followersCount = Column(Integer, default=0)
    followingCount = Column(Integer, default=0)
    isBlocked = Column(Boolean, default=False)

    createdAt = Column(DateTime, default=datetime.now(), nullable=False)
    updatedAt = Column(DateTime, default=None, onupdate=datetime.now())


class Follows(Base):
    __tablename__ = 'follows'

    followerId = Column(Integer, ForeignKey('users.id'), nullable=False)
    followeeId = Column(Integer, ForeignKey('users.id'), nullable=False)
    createdAt = Column(DateTime, default=datetime.now(), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('followerId', 'followeeId'),
    )


class tag(enum.Enum):
    veg = 'veg'
    nonveg = 'non-veg'


class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipeName = Column(String(255), nullable=False)
    description = Column(String(500))
    recipeType = Column(Enum(tag), nullable=False)
    peopleCount = Column(Integer, default=1)
    likesCount = Column(Integer, default=0)
    forkedCount = Column(Integer, default=0)
    isDeleted = Column(Boolean, default=False)
    isHide = Column(Boolean, default=False)

    createdAt = Column(DateTime, default=datetime.now(), nullable=False)
    updatedAt = Column(DateTime, default=None, onupdate=datetime.now())
    deletedAt = Column(DateTime)


class ForkedRecipes(Base):
    __tablename__ = 'forked_recipes'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipeId = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    recipeName = Column(String(255), nullable=False)
    description = Column(String(500))
    recipeType = Column(Enum(tag), nullable=False)
    peopleCount = Column(Integer, default=1)

    createdAt = Column(DateTime, default=datetime.now(), nullable=False)
    updatedAt = Column(DateTime, default=None, onupdate=datetime.now())


class Ingredients(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True, index=True)
    ingredientName = Column(String(255), nullable=False)

    createdAt = Column(DateTime, default=datetime.now(), nullable=False)
    updatedAt = Column(DateTime, default=None, onupdate=datetime.now())


class WeightUnit(enum.Enum):
    gram = "gram"
    kilogram = "kilogram"
    liter = "liter"
    mililiter = "mililiter"
    teaspoon = "teaspoon"
    tablespoon = "tablespoon"
    cup = "cup"
    piece = "piece"


class RecipeIngredients(Base):
    __tablename__ = 'recipe_ingredients'

    id = Column(Integer, primary_key=True, index=True)
    ingredientId = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    recipeId = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(Enum(WeightUnit), nullable=False)

    createdAt = Column(DateTime, default=datetime.now(), nullable=False)
    updatedAt = Column(DateTime, default=None, onupdate=datetime.now())


class RecipeComments(Base):
    __tablename__ = 'recipe_comments'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    recipeId = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    parentCommentId = Column(Integer, ForeignKey('recipe_comments.id'))

    createdAt = Column(DateTime, default=datetime.now(), nullable=False)
    updatedAt = Column(DateTime, default=None, onupdate=datetime.now())

    __table_args__ = {'extend_existing': True}

class RecipeLikes(Base):
    __tablename__ = 'recipe_likes'

    userId = Column(Integer, ForeignKey('users.id'))
    recipeId = Column(Integer, ForeignKey('recipes.id'))

    createdAt = Column(DateTime, default=datetime.now(), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('userId', 'recipeId'),
    )


class CookingHistory(Base):
    __tablename__ = 'cooking_historys'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipeId = Column(Integer, ForeignKey('recipes.id'), nullable=False)

    createdAt = Column(DateTime, default=datetime.now(), nullable=False)
    updatedAt = Column(DateTime, default=None, onupdate=datetime.now())
    
    __table_args__ = (
        {'extend_existing': True},
    )

class VisiblityEnum(enum.Enum):
    public = 'public'
    private = 'private'


class Wishlists(Base):
    __tablename__ = 'wishlists'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipeId = Column(Integer, ForeignKey('recipes.id'), nullable=False)

    visibility = Column(Enum(VisiblityEnum), default=VisiblityEnum.private)

    createdAt = Column(DateTime, default=datetime.now(), nullable=False)
    updatedAt = Column(DateTime, default=None, onupdate=datetime.now())
