from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Trigger_time:
    mouth: list[int] = field(default_factory=list)
    week_day: list[int] = field(default_factory=list)
    mouth_day: list[int] = field(default_factory=list)
    hour: int = 0
    minute: int = 0

    def to_dict(self):
        return {
            "mouth": self.mouth,
            "week_day": self.week_day,
            "mouth_day": self.mouth_day,
            "hour": self.hour,
            "minute": self.minute   
        }


@dataclass
class Task:
    id: int
    title: str
    description: str
    time: str

    code: str
    trigger_time_list: list[Trigger_time] = field(default_factory=list)
    immediately: bool = False
    completed: bool = False
    trigger_count: int = 0
    target_count: int = 0
    
    is_send: bool = False
    send_url: str | None = None
    send_token: str | None = None

    def __post_init__(self):
        if isinstance(self.trigger_time_list, str):
            self.trigger_time_list = eval(self.trigger_time_list)


    def done(self):
        self.completed = True


    def to_tuple(self):
        return (
            self.title,
            self.description,
            self.time,
            self.code,
            str(self.trigger_time_list),
            self.immediately,
            self.completed,
            self.trigger_count,
            self.target_count,
            self.is_send,
            self.send_url,
            self.send_token,
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "time": self.time,
            "code": self.code,
            "trigger_time_list": [trigger for trigger in self.trigger_time_list],
            "immediately": self.immediately,
            "completed": self.completed,
            "trigger_count": self.trigger_count,
            "target_count": self.target_count,
            "is_send": self.is_send,
            "send_url": self.send_url,
            "send_token": self.send_token
        }