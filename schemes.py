from pydantic import BaseModel
from datetime import datetime, time


class Todo(BaseModel):
    id:int
    plan:str
    description:str
    created_date:datetime
    status:bool
    user_id:int


    # model_config = {
    #     "json_schema_extra":{
    #         "examples":[
    #             {
    #                 "id":1,
    #                 "plan":"swimming",
    #                 "description":"swimming"
    #
    #
    #             }
    #         ]
    #     }
    # }


class TodoPost(BaseModel):
    plan:str
    description:str
    status:bool