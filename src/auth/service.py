from sqlmodel import Session, select
from .schemas import UserCreate
from db.models import User
from .utils import generate_passwd_hash
# 1. IMPORT CUSTOM EXCEPTION
from errors import UserAlreadyExists 

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str):
        statement = select(User).where(User.email == email)
        result = self.session.exec(statement)
        return result.first()

    def user_exists(self, email: str) -> bool:
        user = self.get_user_by_email(email)
        return user is not None

    def create_user(self, user_data: UserCreate):
        # 2. CHECK AND RAISE CUSTOM EXCEPTION
        if self.user_exists(user_data.email):
            raise UserAlreadyExists()

        hashed_pwd = generate_passwd_hash(user_data.password)

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=hashed_pwd,
            is_verified=False
        )

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        
        return new_user