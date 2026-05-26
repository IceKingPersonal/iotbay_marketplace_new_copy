from database import get_db

#Used for User Access Management Feature
class AccessLogModel:


    @staticmethod
    def create_login_log(user_id):
        #Creates a new access log when a user logs in. 
        db = get_db()

        cursor = db.execute("""
            INSERT INTO user_access_logs (user_id)
            VALUES (?)
        """, (user_id,))

        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update_logout_time(log_id):
        #Updates the specific acceess log with the logout time using computer's local time.
        db = get_db()

        db.execute("""
            UPDATE user_access_logs
            SET logout_time = datetime('now', 'localtime')
            WHERE log_id = ?
        """, (log_id,))

        db.commit()

    @staticmethod
    def find_by_user_id(user_id):
        #Finds all access logs for the specific user
        db = get_db()

        logs = db.execute("""
            SELECT *
            FROM user_access_logs
            WHERE user_id = ?
            ORDER BY login_time DESC
        """, (user_id,)).fetchall()

        return logs

    @staticmethod
    def find_by_user_id_and_date(user_id, date):
        #Finds specific user logs via date time format.
        db = get_db()

        logs = db.execute("""
            SELECT *
            FROM user_access_logs
            WHERE user_id = ?
              AND DATE(login_time) = ?
            ORDER BY login_time DESC
        """, (user_id, date)).fetchall()

        return logs

    @staticmethod
    def to_dict(log):
        #Converts one access log row into Dictionary format for easier use.
        return {
            "log_id": log["log_id"],
            "user_id": log["user_id"],
            "login_time": log["login_time"],
            "logout_time": log["logout_time"],
            "created_at": log["created_at"]
        }

    @staticmethod
    def to_list(logs):
        #Converts all SQLite rows into dictionaries for easier use.
        return [AccessLogModel.to_dict(log) for log in logs]