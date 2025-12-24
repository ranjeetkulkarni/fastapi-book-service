from sqlmodel import Session, select
from .schemas import UserCreate
from db.models import User
from .utils import generate_passwd_hash

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str):
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    # ✅ THE FIX: Update definition to accept 'username'
    def user_exists(self, email: str, username: str = None) -> bool:
        # Check if EITHER the email OR the username matches
        statement = select(User).where((User.email == email) | (User.username == username))
        user = self.session.exec(statement).first()
        return True if user else False

    def create_user(self, user_data: UserCreate):
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

    def update_user(self, user: User, update_data: dict):
        for key, value in update_data.items():
            setattr(user, key, value)
            
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user