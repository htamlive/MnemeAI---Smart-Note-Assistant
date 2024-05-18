from dataclasses import dataclass, field
from typing import Optional, List, Dict, Union


@dataclass
class CalendarEvent:
    kind: Optional[str] = None
    etag: Optional[str] = None
    id: Optional[str] = None
    status: Optional[str] = None
    htmlLink: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    colorId: Optional[str] = None

    @dataclass
    class Person:
        id: Optional[str] = None
        email: Optional[str] = None
        displayName: Optional[str] = None
        self: Optional[bool] = None

    creator: Optional[Person] = None
    organizer: Optional[Person] = None

    @dataclass
    class DateTime:
        date: Optional[str] = None
        dateTime: Optional[str] = None
        timeZone: Optional[str] = None

    start: Optional[DateTime] = None
    end: Optional[DateTime] = None
    endTimeUnspecified: Optional[bool] = None
    recurrence: Optional[List[str]] = field(default_factory=list)
    recurringEventId: Optional[str] = None
    originalStartTime: Optional[DateTime] = None
    transparency: Optional[str] = None
    visibility: Optional[str] = None
    iCalUID: Optional[str] = None
    sequence: Optional[int] = None

    @dataclass
    class Attendee:
        id: Optional[str] = None
        email: Optional[str] = None
        displayName: Optional[str] = None
        organizer: Optional[bool] = None
        self: Optional[bool] = None
        resource: Optional[bool] = None
        optional: Optional[bool] = None
        responseStatus: Optional[str] = None
        comment: Optional[str] = None
        additionalGuests: Optional[int] = None

    attendees: Optional[List[Attendee]] = field(default_factory=list)
    attendeesOmitted: Optional[bool] = None

    @dataclass
    class ExtendedProperties:
        private: Optional[Dict[str, str]] = field(default_factory=dict)
        shared: Optional[Dict[str, str]] = field(default_factory=dict)

    extendedProperties: Optional[ExtendedProperties] = None
    hangoutLink: Optional[str] = None

    @dataclass
    class ConferenceData:
        @dataclass
        class CreateRequest:
            requestId: Optional[str] = None

            @dataclass
            class ConferenceSolutionKey:
                type: Optional[str] = None

            conferenceSolutionKey: Optional[ConferenceSolutionKey] = None

            @dataclass
            class Status:
                statusCode: Optional[str] = None

            status: Optional[Status] = None

        createRequest: Optional[CreateRequest] = None

        @dataclass
        class EntryPoint:
            entryPointType: Optional[str] = None
            uri: Optional[str] = None
            label: Optional[str] = None
            pin: Optional[str] = None
            accessCode: Optional[str] = None
            meetingCode: Optional[str] = None
            passcode: Optional[str] = None
            password: Optional[str] = None

        entryPoints: Optional[List[EntryPoint]] = field(default_factory=list)

        @dataclass
        class ConferenceSolution:
            @dataclass
            class Key:
                type: Optional[str] = None

            key: Optional[Key] = None
            name: Optional[str] = None
            iconUri: Optional[str] = None

        conferenceSolution: Optional[ConferenceSolution] = None

        conferenceId: Optional[str] = None
        signature: Optional[str] = None
        notes: Optional[str] = None

    conferenceData: Optional[ConferenceData] = None

    @dataclass
    class Gadget:
        type: Optional[str] = None
        title: Optional[str] = None
        link: Optional[str] = None
        iconLink: Optional[str] = None
        width: Optional[int] = None
        height: Optional[int] = None
        display: Optional[str] = None
        preferences: Optional[Dict[str, str]] = field(default_factory=dict)

    gadget: Optional[Gadget] = None

    anyoneCanAddSelf: Optional[bool] = None
    guestsCanInviteOthers: Optional[bool] = None
    guestsCanModify: Optional[bool] = None
    guestsCanSeeOtherGuests: Optional[bool] = None
    privateCopy: Optional[bool] = None
    locked: Optional[bool] = None

    @dataclass
    class Reminder:
        method: Optional[str] = None
        minutes: Optional[int] = None

    reminders: Optional[Dict[str, Union[bool, List[Reminder]]]] = None

    @dataclass
    class Source:
        url: Optional[str] = None
        title: Optional[str] = None

    source: Optional[Source] = None

    @dataclass
    class WorkingLocationProperties:
        type: Optional[str] = None
        homeOffice: Optional[Union[str, None]] = None

        @dataclass
        class CustomLocation:
            label: Optional[str] = None

        customLocation: Optional[CustomLocation] = None

        @dataclass
        class OfficeLocation:
            buildingId: Optional[str] = None
            floorId: Optional[str] = None
            floorSectionId: Optional[str] = None
            deskId: Optional[str] = None
            label: Optional[str] = None

        officeLocation: Optional[OfficeLocation] = None

    workingLocationProperties: Optional[WorkingLocationProperties] = None

    @dataclass
    class OutOfOfficeProperties:
        autoDeclineMode: Optional[str] = None
        declineMessage: Optional[str] = None

    outOfOfficeProperties: Optional[OutOfOfficeProperties] = None

    @dataclass
    class FocusTimeProperties:
        autoDeclineMode: Optional[str] = None
        declineMessage: Optional[str] = None
        chatStatus: Optional[str] = None

    focusTimeProperties: Optional[FocusTimeProperties] = None

    @dataclass
    class Attachment:
        fileUrl: Optional[str] = None
        title: Optional[str] = None
        mimeType: Optional[str] = None
        iconLink: Optional[str] = None
        fileId: Optional[str] = None

    attachments: Optional[List[Attachment]] = field(default_factory=list)

    eventType: Optional[str] = None

@dataclass
class CalendarEventList:
    kind: Optional[str] = None
    etag: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    updated: Optional[str] = None
    timeZone: Optional[str] = None
    accessRole: Optional[str] = None

    @dataclass
    class Reminder:
        method: Optional[str] = None
        minutes: Optional[int] = None

    defaultReminders: Optional[List[Reminder]] = field(default_factory=list)
    nextPageToken: Optional[str] = None
    nextSyncToken: Optional[str] = None
    items: Optional[List[CalendarEvent]] = field(default_factory=list)
