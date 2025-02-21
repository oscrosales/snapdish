import requests
from gtts import gTTS

import os

class FoodAPI():

    def __init__(self, userInput: str):
        self.foundMeal = False
        for char in userInput: # replace space with _
            if char == ' ':
                char = '_'

        ingredient = "filter.php?i=" + userInput

        self.getAllMeals(ingredient)

    def __str__(self):
        if self.foundMeal == True:
            result = ""
            result += f"Meal: {self.meal_name}\n"
            result += f"Category: {self.meal_category}\n"
            result += f"Area: {self.meal_area}\n"

            result += f"Ingredients: \n"
            for ingredients in self.meal_ingredient:
                result += ingredients
                result += "\n"

            result += f"Instructions: {self.meal_instructions}\n"
            result += f"Image URL: {self.meal_image}\n"

            return result
        else:
            return "No meals found. Try again"

    def getAllMeals(self, ingredient: str):
        url = "https://www.themealdb.com/api/json/v1/1/" + ingredient # searches the web with specific ingredient
        response = requests.get(url)
        data = response.json()

        if data['meals'] != None: # add all meals and id's in a list
            meal = data['meals'][0]
            self.meal_name = []
            self.meal_id = []

            for meal in data['meals']:
                self.meal_name.append(meal['strMeal'])
                self.meal_id.append(meal['idMeal'])


            count = 0   # print all recipes
            for food in self.meal_name:
                foodName = str(count) + ". " + food
                print(foodName)
                count += 1


            while (self.foundMeal == False):
                recipe = input("Please choose the number for the recipe you want to see. \n-->")
                if int(recipe) < len(self.meal_id):
                    foodID = self.meal_id[int(recipe)]
                    self.getMeal(foodID)    # get the specific meal that the user chose

                    self.foundMeal = True
                else:
                    print("No recipe found. Try again.")


        else:
            self.foundMeal = False
            return


    def getMeal(self, foodID: str):
        url1 = "https://www.themealdb.com/api/json/v1/1/lookup.php?i=" + foodID
        response = requests.get(url1)
        data = response.json()


        meal = data['meals'][0]
        self.meal_name = meal['strMeal']
        self.meal_category = meal['strCategory']
        self.meal_area = meal['strArea']
        self.meal_instructions = meal['strInstructions']
        self.meal_image = meal['strMealThumb']

        self.meal_ingredient = []
        for i in range(1, 21):
            ingredient = meal[f'strIngredient{i}']
            if ingredient and ingredient.strip() != "":
                self.meal_ingredient.append(ingredient)

    def getInstructions(self):
        return f"Instructions: {self.meal_instructions}\n"

    def getFoundMeal(self):
        return self.foundMeal


def textToSpeech(food: FoodAPI, foodInstruction: str):
    if food.getFoundMeal() == True:
        language = 'en'
        myobj = gTTS(text = str(foodInstruction), lang = language, slow = False)

        myobj.save("foodInstruction.mp3")

        os.system("open FoodInstruction.mp3")
    else:
        print("Instructions cannot be played")

userInput = input("What ingredient do you have?\n-->")
food = FoodAPI(userInput)
print(food)
textToSpeech(food, food.getInstructions())