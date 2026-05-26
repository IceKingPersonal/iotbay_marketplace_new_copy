from database import get_db


class UserModel:

    #Automatically generates staff ID in format S001, S002 etc.
    @staticmethod
    def generate_staff_id():
        db = get_db()

        #Finds latest staff member with a staff_id
        latest_staff = db.execute("""
            SELECT staff_id
            FROM users
            WHERE role = 'staff'
              AND staff_id IS NOT NULL
            ORDER BY user_id DESC
            LIMIT 1
        """).fetchone()

        #If there are no staff users yet, it creates the first staff_id at S001.
        if latest_staff is None:
            return "S001"

        latest_staff_id = latest_staff["staff_id"]

        #Removes the S from staff ID then converts it to an integer. Adds a 1 to the next staff member and then readds the S at the end.
        try:
            latest_number = int(latest_staff_id[1:])
        except ValueError:
            latest_number = 0

        new_number = latest_number + 1

        return f"S{new_number:03d}"

    @staticmethod
    def create_user(data, password_hash):
        db = get_db()
        
        # Gets the selected account role from the registration form.
        role = data.get("role")

        # If the new user is staff, automatically generate a staff ID.
        if role == "staff":
            staff_id = UserModel.generate_staff_id()
        else:
            #If its not a staff, it must be a customer, therefore do not generate a staff ID.
            staff_id = None

        #Inserts the new user into the users table. Depending on if the user is staff or customer it only saves the necessary fields.
        cursor = db.execute("""
            INSERT INTO users (
                role,
                full_name,
                email,
                password_hash,
                phone,
                address,
                staff_id,
                position
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            role,
            data.get("full_name"),
            data.get("email"),
            password_hash,
            data.get("phone") if role == "customer" else None,
            data.get("address") if role == "customer" else None,
            staff_id,
            data.get("position") if role == "staff" else None
        ))

        db.commit()
        return cursor.lastrowid

    @staticmethod
    def find_by_email(email):
        db = get_db()

        #Finds a user with matching email address.
        user = db.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()
        
        #Returns the user if it finds it. If not it returns nothing.
        return user

    @staticmethod
    def find_by_id(user_id):
        db = get_db()
        #Finds a user with matching user ID
        user = db.execute("""
            SELECT *
            FROM users
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        #Returns the user if it finds it. If not it returns nothing.
        return user

    @staticmethod
    def update_user(user_id, data):
        db = get_db()
        
        #Finds the existing user before updating anything.
        user = UserModel.find_by_id(user_id)

        role = user["role"]

        #Updates customer fields if customer.
        if role == "customer":
            db.execute("""
                UPDATE users
                SET full_name = ?,
                    email = ?,
                    phone = ?,
                    address = ?
                WHERE user_id = ?
            """, (
                data.get("full_name"),
                data.get("email"),
                data.get("phone"),
                data.get("address"),
                user_id
            ))

        #Updates staff fields if staff.
        elif role == "staff":
            db.execute("""
                UPDATE users
                SET full_name = ?,
                    email = ?,
                    position = ?
                WHERE user_id = ?
            """, (
                data.get("full_name"),
                data.get("email"),
                data.get("position"),
                user_id
            ))
        #Saves the updated changes to the database.
        db.commit()
        return True

    @staticmethod
    def cancel_user(user_id):
        db = get_db()
        #Cancels the account by changing user status to inactive. Nothing else is needed here as we need to keep user info in DB.
        db.execute("""
            UPDATE users
            SET status = 'inactive'
            WHERE user_id = ?
        """, (user_id,))

        db.commit()
        return True

    @staticmethod
    def to_dict(user):

        if user is None:
            return None
        #Converts SQLite user row into a dictionary for easier use.
        return {
            "user_id": user["user_id"],
            "role": user["role"],
            "full_name": user["full_name"],
            "email": user["email"],
            "phone": user["phone"],
            "address": user["address"],
            "staff_id": user["staff_id"],
            "position": user["position"],
            "status": user["status"],
            "created_at": user["created_at"]
        }