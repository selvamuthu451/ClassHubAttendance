import os

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "ballast.proxy.rlwy.net"),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", "RNoulnCyqnXmTVWfBTclwxfmgemcofFC"),
    "database": os.getenv("MYSQLDATABASE", "railway"),
    "port": int(os.getenv("MYSQLPORT", 29083))
}
