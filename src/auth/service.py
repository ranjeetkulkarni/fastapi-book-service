from sqlmodel import Session, select
from .schemas import UserCreate
from db.models import User  # <--- CHANGED THIS
from .utils import generate_passwd_hash

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str):
        # SQLModel syntax is slightly different from raw SQLAlchemy
        statement = select(User).where(User.email == email)
        result = self.session.exec(statement)
        return result.first()

    def user_exists(self, email: str) -> bool:
        user = self.get_user_by_email(email)
        return user is not None

    def create_user(self, user_data: UserCreate):
        # 1. Hash the password
        hashed_pwd = generate_passwd_hash(user_data.password)

        # 2. Map Schema to Model 
        # CAREFUL: We map 'password' from schema to 'password_hash' in DB
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=hashed_pwd, # <--- The critical mapping
            is_verified=False
        )

        # 3. Add to DB
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        
        return new_user