from pydantic import BaseModel,field_validator

class UpdateUser(BaseModel):
    user_name:str
    first_name:str
    last_name:str

    @field_validator("first_name","last_name","user_name",mode="before")
    def verify_details(cls,v,field):
        if not isinstance(v,str):
            raise TypeError(f"{field.name} should be type of string")
        
        if not v.strip():
            raise ValueError(f"{field.name} can not be empty")
        
        return v.strip()

