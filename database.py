import sqlite3

from utils import get_dict


class DB:
    def __init__(self, db_path, data, debug):
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        self.con = con
        self.cursor = cursor
        self.debug = debug
        self.init_tables()
        self.init_db_data(data)
        self.db_path = db_path

    def init_db_data(self, data):

        # populate measures
        measures = get_dict(data, 'measures')
        for key, value in measures.items():
            try:
                self.cursor.execute("""INSERT INTO 
                measures(measure_id, measure_name) 
                VALUES (?, ?)""", (key, value))
            except sqlite3.IntegrityError:
                if self.debug:
                    print(key, value, 'exists')
                pass

        self.con.commit()

        # populate ingredients
        ingredients = get_dict(data, 'ingredients')
        for key, value in ingredients.items():
            try:
                self.cursor.execute("""INSERT INTO 
                ingredients(ingredient_id, ingredient_name) 
                VALUES (?, ?)""", (key, value))
            except sqlite3.IntegrityError:
                if self.debug:
                    print(key, value, 'exists')
                pass
        self.con.commit()

        # populate meals
        meals = get_dict(data, 'meals')
        for key, value in meals.items():
            try:
                self.cursor.execute("""INSERT INTO 
                meals(meal_id, meal_name) 
                VALUES (?, ?)""", (key, value))
            except sqlite3.IntegrityError:
                if self.debug:
                    print(key, value, 'exists')
                pass

        self.con.commit()

    def close(self):
        self.con.close()

    def init_tables(self):
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS measures(
        measure_id INTEGER PRIMARY KEY,
        measure_name TEXT UNIQUE
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients(
        ingredient_id INTEGER PRIMARY KEY,
        ingredient_name TEXT NOT NULL UNIQUE
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals(
        meal_id INTEGER PRIMARY KEY,
        meal_name TEXT NOT NULL UNIQUE
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes(
        recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_name TEXT NOT NULL,
        recipe_description TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS serve(
        serve_id INTEGER PRIMARY KEY AUTOINCREMENT,
        meal_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        FOREIGN KEY (meal_id)
            REFERENCES meals (meal_id),
        FOREIGN KEY (recipe_id)
            REFERENCES recipes (recipe_id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS quantity(
        quantity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        quantity INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        measure_id INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        FOREIGN KEY (recipe_id)
            REFERENCES recipes (recipe_id),
        FOREIGN KEY (measure_id)
            REFERENCES measures (measure_id),
        FOREIGN KEY (ingredient_id)
            REFERENCES ingredients (ingredient_id)
        )
        """)

        self.con.commit()

    def insert_recipe(self, recipe, meals, quantities):
        try:
            recipe_id = self.cursor.execute(
                'INSERT INTO recipes(recipe_name, recipe_description) VALUES (?, ?)',
                recipe).lastrowid
            print(recipe_id)
            for meal in meals:
                self.cursor.execute(
                    'INSERT INTO serve(recipe_id, meal_id) VALUES (?, ?)', (recipe_id, int(meal)))
            for q in quantities:
                self.cursor.execute(
                    'INSERT INTO quantity(quantity, recipe_id, measure_id, ingredient_id) VALUES (?, ?, ?, ?)',
                    (q['quantity'], recipe_id, q['measure'], q['ingredient']))

        except sqlite3.IntegrityError as e:
            print(e)
            pass

        self.con.commit()

    def get_meals(self):

        self.cursor.execute('SELECT * FROM meals')
        return self.cursor.fetchall()

    def get_measure(self, measure):

        if measure == '':
            self.cursor.execute("SELECT * FROM measures WHERE measure_name = ? ;", (measure,))
        else:
            self.cursor.execute("SELECT * FROM measures WHERE measure_name LIKE ? ;", ("{}%".format(measure),))
        return self.cursor.fetchall()

    def get_ingredient(self, ingredient):

        self.cursor.execute("SELECT * FROM ingredients WHERE ingredient_name LIKE ? ;", ("{}%".format(ingredient),))
        return self.cursor.fetchall()

    def search_recipes(self, meal_names, ingredient_names):
        self.cursor.execute("""SELECT recipes.recipe_id, recipes.recipe_name FROM ingredients 
                               INNER JOIN quantity
                                    ON ingredients.ingredient_id = quantity.ingredient_id
                                INNER JOIN recipes
                                    ON recipes.recipe_id = quantity.recipe_id
                                WHERE ingredients.ingredient_name IN ({})
                                GROUP BY recipes.recipe_id 
                                HAVING COUNT(DISTINCT ingredients.ingredient_id) = ?
                                INTERSECT
                                SELECT recipes.recipe_id, recipes.recipe_name FROM meals
                                INNER JOIN serve
                                    ON serve.meal_id = meals.meal_id
                                INNER JOIN recipes
                                    ON serve.recipe_id = recipes.recipe_id
                                WHERE meals.meal_name IN ({})
                                ;""".format(get_bindings(ingredient_names),
                                            get_bindings(meal_names)),
                            (*ingredient_names, len(ingredient_names), *meal_names))
        return self.cursor.fetchall()


def get_bindings(args):
    return '?, ' * (len(args) - 1) + '?'
