#!/usr/bin/env python3

import sys, os, requests


def help_message():
    """Displays the help message for the passive tool."""
    print(
        """
Welcome to passive v1.0.0

OPTIONS:
    -fn         Search with full-name
    -ip         Search with ip address
    -u          Search with username
    """
    )


def search_with_full_name(full_name, save_location):
    """This function takes a full name and a file path and searches for the full name using the Ratsit API."""
    try:
        res = requests.post(
            "https://www.ratsit.se/api/search/person",
            json={
                "who": full_name,
                "age": ["16", "120"],
                "phoneticSearch": "true",
                "companyName": "",
                "orgNr": "",
                "firstName": "",
                "lastName": "",
                "personNumber": "",
                "phone": "",
                "address": "",
                "postnr": "",
                "postort": "",
                "kommun": "",
                "page": 1,
                "url": "",
            },
        )
        data = res.json()["person"]["hits"]
        for person in data:
            ## Print the person
            address = person["streetAddress"]
            city = person["city"]
            # Get postal code from the address
            postal_code = requests.get(
                f"https://postnummer.me/search?query={address},{city}"
            ).json()["data"][0]["postal_code"]

            # Some chenaningans to get the phone number
            person_url = person["personUrl"]
            person_data = requests.get(person_url).text
            phone = person_data.split("tel:")[1].split('"')[0]
            # Get the first and last name from the person object
            first_name = person["firstName"].split(" ")[0]
            last_name = person["lastName"]
            # Make sure it's perfect matches
            if (
                first_name.lower() not in full_name.lower()
                or last_name.lower() not in full_name.lower()
            ):
                continue
            try:
                with open(save_location, "w") as file:
                    file.write(f"First name:\t{first_name}\n")
                    file.write(f"Last name:\t{last_name}\n")
                    file.write(f"Address:\t{address}\n")
                    file.write(f"\t\t{postal_code} {city}\n")
                    file.write(f"Phone:\t\t{phone}\n")
                    # Scary cuz Sweden fuqqd
                    file.write(f"Scary URL:\t{person['personUrl']}\n")
                with open(save_location, "r") as file:
                    print(file.read())
            except Exception as e:
                print("Error while writing to file:", e)

    except Exception as e:
        print("Error while searching:", e)
    print("Saved in", save_location)


def search_with_ip(ip_address, save_location):
    """This function takes an IP address and a file path and searches for the IP address across the internet.

    It utilizes http://ip-api.com web service to find the ISP, city, latitude, and longitude of the IP address.
    """
    # Dummy data for demonstration
    res = requests.get(f"http://ip-api.com/json/{ip_address}")
    data = res.json()
    isp = data["isp"]
    city = data["city"]
    lat = data["lat"]
    lon = data["lon"]
    try:
        with open(save_location, "w") as file:
            file.write(f"ISP:\t\t{isp}\n")
            file.write(f"City Lat/Lon:\t({lat}) / ({lon})")
        with open(save_location, "r") as file:
            print(file.read())
        print("Saved in", save_location)
    except Exception as e:
        print("Error while writing to file:", e)


def search_with_username(username, save_location):
    """
    This function takes a username and a file path and searches for the username across social media platforms.

    It utilizes the sherlock tool to find usernames across social media platforms.

    The results are written to a file at the specified location.

    Social media platforms searched:
        - Reddit
        - Instagram
        - Twitter
        - StreamGroup
        - GitHub
        - LeetCode
        - Minecraft
        - VK
        - Spotify
    """
    # Starts a subprocess which runs sherlock, a tool to find usernames across social media
    res = os.popen(
        f"cd sherlock && python sherlock {username} \
            --site Reddit \
            --site Instagram \
            --site Twitter \
            --site StreamGroup \
            --site GitHub \
            --site LeetCode \
            --site Minecraft \
            --site VK \
            --site Spotify \
            --print-all"
    ).read()
    found = []
    not_found = []
    for line in res.split("\n"):
        if "+" in line:
            found.append(line.split(" ")[1][:-1])
        if "-" in line:
            not_found.append(line.split(" ")[1][:-1])
    try:
        with open(save_location, "w") as file:
            for platform in found:
                file.write(
                    f"{platform}:\t{'yes'}\n"
                    if len(platform) > 6
                    else f"{platform}:\t\t{'yes'}\n"
                )
            for platform in not_found:
                file.write(
                    f"{platform}:\t{'no'}\n"
                    if len(platform) > 6
                    else f"{platform}:\t\t{'no'}\n"
                )
        with open(save_location, "r") as file:
            print(file.read())
        print("Saved in", save_location)
    except Exception as e:
        print("Error while writing to file:", e)


def get_unique_filename(save_location):
    """This function takes a file path and returns a unique file path by appending a number to the end of the file name."""
    base_name = os.path.splitext(save_location)[0]
    extension = os.path.splitext(save_location)[1]
    counter = 2

    while os.path.exists(save_location):
        save_location = f"{base_name}{counter}{extension}"
        counter += 1

    return save_location


def main():
    if len(sys.argv) == 1 or sys.argv[1] == "--help":
        help_message()
        os._exit(0)
    save_location = get_unique_filename("result.txt")
    try:
        match sys.argv[1]:
            case "-fn":
                search_with_full_name(sys.argv[2], save_location)
            case "-ip":
                search_with_ip(sys.argv[2], save_location)
            case "-u":
                search_with_username(sys.argv[2], save_location)
            case _:
                print("Invalid option")
                help_message()
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
