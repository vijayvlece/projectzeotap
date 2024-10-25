
import mysql.connector
from mysql.connector import Error
import json  # Standard library for JSON handling

class DBConnection:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self.cur = None

    def connect(self):
        """Establish a connection to the MySQL database."""
        if self.conn is None:
            try:
                self.conn = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                self.cur = self.conn.cursor()
            except Error as e:
                print(f"Error connecting to the database: {e}")
                raise  # Raising to ensure connection errors are caught for retry or adjustment.

    def close(self):
        """Close the database connection and cursor."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def store_rule(self, rule_string, ast_json):
        """Store the rule and its AST in the MySQL database."""
        self.connect()
        try:
            insert_query = """
            INSERT INTO rules (rule_string, ast)
            VALUES (%s, %s)
            """
            ast_json_str = json.dumps(ast_json) if isinstance(ast_json, dict) else ast_json
            self.cur.execute(insert_query, (rule_string, ast_json_str))
            self.conn.commit()
            return self.cur.lastrowid  # Return the ID of the inserted row
        except Error as e:
            print(f"Error storing rule: {e}")
            self.conn.rollback()  # Rollback only in case of an exception
            raise
        finally:
            self.close()

    def load_rule(self, rule_id):
        """Load the rule and its AST from the MySQL database."""
        self.connect()
        try:
            select_query = "SELECT rule_string, ast FROM rules WHERE id = %s"
            self.cur.execute(select_query, (rule_id,))
            result = self.cur.fetchone()

            if result:
                rule_string, ast_json_str = result
                ast_json = json.loads(ast_json_str)
                return rule_string, ast_json
            return None, None
        except Error as e:
            print(f"Error loading rule: {e}")
            raise
        finally:
            self.close()

class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.node_type = node_type
        self.left = left
        self.right = right
        self.value = value

def create_rule(rule_string):
    """Parse the rule string and convert it to an AST."""
    # Placeholder logic for demonstration
    # Replace this with actual parsing logic to create an AST
    return Node("AND", 
                left=Node("condition", value="age > 30"), 
                right=Node("condition", value="salary > 50000"))

def combine_rules(rule1, rule2):
    """Combine two rules (ASTs) using an AND operator."""
    return Node("AND", left=rule1, right=rule2)

def evaluate_rule(ast, data):
    """Evaluate the AST against provided user data."""
    if ast.node_type == "AND":
        return evaluate_rule(ast.left, data) and evaluate_rule(ast.right, data)
    elif ast.node_type == "OR":
        return evaluate_rule(ast.left, data) or evaluate_rule(ast.right, data)
    elif ast.node_type == "condition":
        try:
            attribute, operator, value = ast.value.split(" ")
            if attribute in data:
                if operator == ">":
                    return data[attribute] > int(value)
                elif operator == "<":
                    return data[attribute] < int(value)
                elif operator == "=":
                    return data[attribute] == int(value)
            return False
        except (IndexError, ValueError) as e:
            print(f"Error evaluating condition: {e}")
            return False
    return False

def ast_to_json(ast):
    """Convert AST to JSON format for storage."""
    if ast is None:
        return None
    return {
        "node_type": ast.node_type,
        "left": ast_to_json(ast.left),
        "right": ast_to_json(ast.right),
        "value": ast.value
    }

def json_to_ast(json_data):
    """Convert JSON back to AST."""
    if json_data is None:
        return None
    return Node(
        node_type=json_data["node_type"],
        left=json_to_ast(json_data.get("left")),
        right=json_to_ast(json_data.get("right")),
        value=json_data.get("value")
    )

# Example Usage
if __name__ == "__main__":
    db = DBConnection(host='localhost', database='your_database', user='your_user', password='your_password')

    # Create a rule and store it
    rule_string = "((age > 30 AND salary > 50000))"
    ast = create_rule(rule_string)
    ast_json = ast_to_json(ast)
    try:
        rule_id = db.store_rule(rule_string, ast_json)
        print(f"Stored rule with ID: {rule_id}")

        # Load the rule back
        loaded_rule_string, loaded_ast_json = db.load_rule(rule_id)
        loaded_ast = json_to_ast(loaded_ast_json)
        print(f"Loaded rule: {loaded_rule_string}")

        # Evaluate the rule
        user_data = {"age": 35, "salary": 60000}
        result = evaluate_rule(loaded_ast, user_data)
        print(f"Rule evaluation result: {result}")

    except Error as e:
        print("Database operation failed. Check your credentials and database setup.")
