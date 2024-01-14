import dataclasses
import datetime
import enum
import typing

import pytz
import requests


@dataclasses.dataclass
class ClockifyConfig:
    api_key: str


@dataclasses.dataclass
class TimeEntryFilter:
    start: typing.Optional[str] = None
    end: typing.Optional[str] = None


@dataclasses.dataclass
class ClockifyTimeEntry:
    description: str
    started: datetime.datetime
    ended: datetime.datetime
    duration: datetime.timedelta

    # we need it to convert it into name later
    project_id: str
    entry_id: str


DataType = typing.TypeVar("DataType")
NewDataType = typing.TypeVar("NewDataType")


class ResultErrorType(enum.Enum):
    server_error = "server error"
    client_error = "client error"
    data_error = "data error"


@dataclasses.dataclass
class ResultError:
    message: typing.Optional[str]
    error_type: ResultErrorType


@dataclasses.dataclass
class Result(typing.Generic[DataType]):
    data: typing.Optional[DataType] = None
    error: typing.Optional[ResultError] = None

    def transform(self, fn: typing.Callable[[DataType], NewDataType]) -> "Result[NewDataType]":
        if isinstance(self, ErrorResult):
            return self

        return SuccessResult(fn(self.data))


class SuccessResult(Result[DataType]):
    def __init__(self, data: DataType):
        self.data = data


class ErrorResult(Result):
    def __init__(self, result_error: ResultError):
        self.error = result_error


class Client:
    def __init__(self, config: ClockifyConfig):
        self.config = config
        self.base_url = "https://api.clockify.me/api/v1"

    @property
    def headers(self):
        return {
            "x-api-key": self.config.api_key
        }

    def time_entries(
        self,
        workspace_id: str,
        user_id: str,
        time_filter: typing.Optional[TimeEntryFilter] = None
    ) -> Result[typing.List[ClockifyTimeEntry]]:

        try:

            resp = requests.get(
                f"{self.base_url}/workspaces/{workspace_id}/user/{user_id}/time-entries",
                headers=self.headers,
                params=dataclasses.asdict(time_filter) if time_filter else None
            )

            if 400 < resp.status_code < 500:
                return ErrorResult(ResultError(resp.text, ResultErrorType.data_error))

            if resp.status_code > 500:
                return ErrorResult(ResultError(resp.text, ResultErrorType.server_error))

            data = resp.json()
            entries = [self._parse_time_entry(entry) for entry in data]
            return SuccessResult(entries)

        except Exception as e:
            return ErrorResult(ResultError(str(e), ResultErrorType.client_error))

    def _parse_time_entry(self, entry) -> ClockifyTimeEntry:
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        start_str = entry["timeInterval"]["start"]
        end_str = entry["timeInterval"]["end"]
        started = datetime.datetime.strptime(start_str, fmt).replace(tzinfo=pytz.UTC)
        ended = datetime.datetime.strptime(end_str, fmt).replace(tzinfo=pytz.UTC)

        return ClockifyTimeEntry(
            description=entry["description"],
            started=started,
            ended=ended,
            duration=ended - started,
            project_id=entry["projectId"],
            entry_id=entry["id"],
        )

