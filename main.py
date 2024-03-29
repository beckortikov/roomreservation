from datetime import datetime
from db import create_connection
from dataclasses import dataclass

today = datetime.today().date()
conn = create_connection()


@dataclass
class Person:
    name: str
    email: str
    phone: int


def get_room_avaibility(room_id, start_time, end_time):
    """Get information about room avaibility to reserve.

    Args:
        room_id (int): Number of reserving room
        start_time (str): Start reservation time
        end_time (str): End of reservation time

    Returns:
        int, str: It returns avaibility o froom
    """
    if check_giving_arguments(room_id, start_time, end_time):
        request_ = request_to_databse(room_id, start_time, end_time)

        if request_.fetchone():
            request_.close()
            return get_reserved_person(room_id, start_time, end_time)
        else:
            return (
                f"You can reserve office {room_id}" f"\nfrom {start_time} to {end_time}"
            )
    else:
        return (
            "Please be sure that you"
            + "\ngiving room_id as int and"
            + "\nstart_time and end_time as str."
        )


def check_giving_arguments(room_id, start_time, end_time):
    """Checking giving arguments to room avaibility"""
    if (
        isinstance(room_id, int)
        and isinstance(start_time, str)
        and isinstance(end_time, str)
    ):
        return True
    else:
        return False


def request_to_databse(room_id, start_time, end_time):
    """Requesting to database. Is there any available room.

    Args:
        room_id (int): Number of reserving room
        start_time (str): Start reservation time
        end_time (str): End of reservation time

    Returns:
        sqlite_cursor: Returns respons from database
    """

    if check_giving_arguments(room_id, start_time, end_time):
        cursor = conn.cursor()
        query_response = cursor.execute(
            """SELECT number 
                    FROM office 
                    WHERE number = ? 
                        AND (start_time = ? 
                        OR end_time = ?);""",
            (
                room_id,
                start_time,
                end_time,
            ),
        )
        return query_response
    else:
        return False


def get_reserved_person(room_id, start_time, end_time):
    """Returns person by whom reserved"""
    cursor = conn.cursor()
    query_response = cursor.execute(
        """SELECT name, start_time, end_time 
                FROM person 
                    INNER JOIN office 
                    ON person.id = office.person_id
                        WHERE office.number = ? 
                            AND (office.start_time = ? 
                            OR office.end_time =?)""",
        (
            room_id,
            start_time,
            end_time,
        ),
    )
    all_responses = query_response.fetchone()
    if all_responses:
        (
            name,
            resp_start_time,
            resp_end_time,
        ) = all_responses

        return (
            f"Sorry, you can't reserve office {room_id}."
            f"\nBecause office reserved by {name}"
            f"\nfrom {resp_start_time} to {resp_end_time}"
        )

    conn.commit()
    conn.close()


def reserve(person, room_id, start_time, end_time):
    """Reserving a room by giving arguments

    Args:
        person (class): Instance of a class Person
        room_id (int): Number of reserving room
        start_time (str): Start reservation time
        end_time (str): End of reservation time

    Returns:
        int, str: Informing about reservation
    """
    if check_giving_arguments(room_id, start_time, end_time):
        cursor = conn.cursor()
        room_id_query = request_to_databse(room_id, start_time, end_time)
        get_room_id = room_id_query.fetchall()

        if get_room_id:
            return print(get_reserved_person(room_id, start_time, end_time))
        elif get_room_id is None:
            reserve_is_none_update(person, room_id, start_time, end_time)
        else:
            cursor.execute(
                "INSERT INTO person VALUES (?, ?, ?, ?)",
                (
                    None,
                    person.name,
                    person.email,
                    person.phone,
                ),
            )
            cursor.execute(
                """INSERT INTO office
                    VALUES (?, ?, (SELECT id 
                    FROM person WHERE name = ?), ?, ?, ?)""",
                (
                    None,
                    room_id,
                    person.name,
                    start_time,
                    end_time,
                    today,
                ),
            )

            print(
                f"{person.name} you successfully reserved"
                f"\noffice №{room_id} from {start_time}"
                f"\nto {end_time}."
            )
    else:
        return (
            "Please be sure that you"
            + "\ngiving room_id as int and"
            + "\nstart_time and end_time as str."
        )

    conn.commit()
    conn.close()


def reserve_is_none_update(person, room_id, start_time, end_time):
    """If room value doesn't exist updating"""
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO person 
            VALUES (?, ?, ?, ?)""",
        (
            None,
            person.name,
            person.email,
            person.phone,
        ),
    )
    cursor.execute(
        """UPDATE office
                SET number = ? person_id = (SELECT id
                    FROM person 
                    WHERE name = ?),
                start_time = ?, end_time = ?, date = ?""",
        (
            room_id,
            person.name,
            start_time,
            end_time,
            today,
        ),
    )

    conn.commit()
    conn.close()


def send_email(person):
    """Returning an information to person"""
    if isinstance(person, Person):
        cursor = conn.cursor()
        query = cursor.execute(
            """SELECT  date, start_time, 
                end_time, number, email, phone 
                FROM person 
                    INNER JOIN office 
                        ON person.id = office.person_id
                            WHERE office.person_id = (SELECT id 
                            FROM person 
                                WHERE name = ?);""",
            (person.name,),
        )

        date_, start_time, end_time, room_number, email, phone = query.fetchone()

        print(
            f"To {email} and {phone}:"
            f"\nYou reserved office {room_number}"
            f"\nfrom {start_time} to {end_time}"
            f"\nat {date_}"
        )

        conn.commit()
        conn.close()
    else:
        raise TypeError("Giving argument must be instance of a class Person")


if __name__ == "__main__":
    person1 = Person("Sasha", "sasha@gmail.com", 7925864874)
    person2 = Person("Ruslan", "ruslan@gmai.com", 759456416)
    person3 = Person("Karim", "karim@gmai.com", 759448856)
    person6 = Person("Azim", "azim@alif.tj", 95659989)
    person7 = Person("Damir", "damir@gmail.com", 87546547998)
    print(get_room_avaibility("1", "08:00", "09:00"))
    reserve(person7, 1, "08:00", "09:00")
    send_email(person7)
