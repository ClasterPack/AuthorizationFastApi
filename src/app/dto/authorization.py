from typing import Optional

from pydantic import BaseModel, EmailStr, model_validator, Field

class UpdateTokenDTO(BaseModel):
    token: str


class CreateUserDTO(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class TokenDTO(BaseModel):
    access_token: str
    token_type: str
    info: Optional[str]


class LoginUserDTO(BaseModel):
    username: Optional[str] = Field(
        default=None,
        description="Имя пользователя. Укажите либо username, либо email, но не оба."
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Email пользователя. Укажите либо email, либо username, но не оба."
    )
    password: str = Field(..., description="Пароль пользователя.")

    @model_validator(mode="after")
    def check_username_xor_email(self):
        if bool(self.username) == bool(self.email):
            raise ValueError('You must provide either username or email, but not both.')
        return self

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "username": "myuser",
                    "password": "secret"
                },
                {
                    "email": "user@example.com",
                    "password": "secret"
                }
            ]
        }

class UpdatePasswordDTO(LoginUserDTO):
    new_password: str = Field(..., description="Новый пароль пользователя.")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "username": "StringUsername",
                    "password": "StringPassword",
                    "new_password": "<PASSWORD>",
                },
                {
                    "email": "user@example.com",
                    "password": "stringPassword",
                    "new_password": "string<PASSWORD>",
                }
            ]
        }

class UserUpdateFields(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field(cls, self):
        if not any([self.username, self.email, self.password, self.first_name, self.last_name]):
            raise ValueError("At least one field must be provided for update.")
        return self

class UpdateUserDTO(LoginUserDTO):
    updates: UserUpdateFields = Field(..., description="Поля для обновления пользователя")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "username": "myuser",
                    "password": "secret",
                    "updates": {
                        "email": "new@email.com",
                        "first_name": "NewName"
                    }
                },
                {
                    "email": "user@example.com",
                    "password": "secret",
                    "updates": {
                        "password": "newpassword"
                    }
                }
            ]
        }