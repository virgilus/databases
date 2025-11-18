import yaml
import hashlib
from typing import Dict, Any

from sqlalchemy import create_engine as sqlalchemy_create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def load_yaml(filepath) -> Dict[str, Any]:
    """Load YAML file and return a dict. """
    with open(filepath, 'r') as file:
        yaml_dict = yaml.safe_load(file) or {}
    return yaml_dict

# Global caching of params and secrets
params = load_yaml('params.yaml')
secrets = load_yaml('secrets.yaml')

def get_engine(params: Dict[str, Any]=params, secrets: Dict[str, Any] | None = secrets, port=3306):
    """Return a SQLAlchemy Engine for MySQL using provided or cached secrets. """
    url = (
        f"mysql+pymysql://{secrets['user']}:{secrets['password']}@"
        f"{params['host']}:{port}/{params['dbname']}"
        "?ssl=true&ssl_verify_cert=false&ssl_verify_identity=false"
        # f"?ssl_ca=&ssl_disabled=false"
    )
    return sqlalchemy_create_engine(url)

def hash_password(password: str) -> str:
    """Hash a password using SHA-256. """
    return hashlib.sha256(password.encode()).hexdigest()

def insert_user(username: str, password: str, email: str | None = None) -> bool:
    """Insert a user row into the users table.

    Assumes a table `users` with columns (username, password_hash, email).
    Returns True if insertion succeeded, False otherwise.
    """
    try:
        engine = get_engine()
    except (FileNotFoundError, KeyError) as e:
        print(f"Engine creation failed: {e}")
        return False

    pw_hash = hash_password(password)
    stmt = text(
        "INSERT INTO users (username, password_hash, email) VALUES (:u, :p, :e)"
    )
    params = {"u": username, "p": pw_hash, "e": email}
    

    try:
        with engine.begin() as conn:  # begin() handles commit/rollback
            conn.execute(stmt, params)
        print("User inserted successfully.")
        return True
    except SQLAlchemyError as e:
        print(f"Insertion error: {e}")
        return False
    
def login(username: str, password: str) -> bool:
    """Check user credentials against the users table.
    Returns True if credentials are valid, False otherwise.
    """
    try:
        engine = get_engine()
    except (FileNotFoundError, KeyError) as e:
        print(f"Engine creation failed: {e}")
        return False

    pw_hash = hash_password(password)
    stmt = text(
        "SELECT COUNT(*) AS user_count FROM users WHERE username = :u AND password_hash = :p"
    )
    params = {"u": username, "p": pw_hash}

    try:
        with engine.connect() as conn:
            result = conn.execute(stmt, params)
            row = result.fetchone()
            if row[0] == 1:
                print("Login successful.")
                return True
            else:
                print("Invalid credentials.")
                return False
    except SQLAlchemyError as e:
        print(f"Login error: {e}")
        return False