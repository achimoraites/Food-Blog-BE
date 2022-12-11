import argparse

from database import DB

parser = argparse.ArgumentParser()

parser.add_argument("db_path")
parser.add_argument("-i", "--ingredients", type=str, default='')
parser.add_argument("-m", "--meals", type=str, default='')

args = parser.parse_args()


data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

db = DB(args.db_path, data, False)

search_ingredients = args.ingredients.split(',')
search_meals = args.meals.split(',')
if args.ingredients and args.meals:
    recipes = db.search_recipes(search_meals, search_ingredients)
    if len(recipes):
        print('Recipes selected for you:', ', '.join([recipe[1] for recipe in recipes]))
    else:
        print('There are no such recipes in the database.')
else:
    meals = db.get_meals()
    meal_options = " ".join(["{}) {}".format(m[0], m[1]) for m in meals])
    print('Pass the empty recipe name to exit')
    while True:
        try:
            name = input('Recipe name:')
            if len(name) == 0:
                break
            description = input('Recipe description:')
            print(meal_options)
            meals = input('Enter proposed meals separated by a space:').split(' ')
            quantities = list()
            while True:
                ingredient_input = input('Input quantity of ingredient <press enter to stop>:')
                ingredient_args = ingredient_input.split(' ')
                measures = list()
                ingredients = list()
                quantity = 0
                if ingredient_input == '':
                    break
                elif len(ingredient_args) == 2:
                    quantity, ingredient = ingredient_args
                    measures = db.get_measure('')
                    ingredients = db.get_ingredient(ingredient)

                elif len(ingredient_args) == 3:
                    quantity, measure, ingredient = ingredient_args
                    measures = db.get_measure(measure)
                    ingredients = db.get_ingredient(ingredient)

                if len(measures) != 1:
                    print('The measure is not conclusive!')
                    continue
                if len(ingredients) != 1:
                    print('The ingredient is not conclusive!')
                    continue

                quantities.append({
                    'quantity': int(quantity),
                    'measure': measures.pop(0)[0],
                    'ingredient': ingredients.pop(0)[0]
                })

            db.insert_recipe((name, description), meals, quantities)
        except Exception as e:
            print(e)

db.close()
