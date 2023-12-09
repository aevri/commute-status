import argparse
import json
import requests

# https://raildata.org.uk/dashboard/dataProduct/P-9a01dd96-7211-4912-bcbb-c1b5d2e35609/overview
API_URL = "https://api1.raildata.org.uk/1010-live-departure-board-dep/LDBWS/api/20220120/GetDepBoardWithDetails"


def query_next_departures(source, destination, api_key):
    params = {
        "filterCrs": destination,
    }

    headers = {
        "x-apikey": api_key,
    }

    response = requests.get(f"{API_URL}/{source}", params=params, headers=headers)
    data = response.json()

    return data


def main():
    parser = argparse.ArgumentParser(description="Commute Status")
    parser.add_argument("source", help="Source location")
    parser.add_argument("destination", help="Destination location")
    parser.add_argument("api_key", help="API key")
    parser.add_argument(
        "--dev-mode",
        choices=["save", "load", "normal"],
        default="normal",
        help="Development mode",
    )

    args = parser.parse_args()

    if args.dev_mode != "load":
        data = query_next_departures(args.source, args.destination, args.api_key)
        if args.dev_mode == "save":
            json.dump(data, open("comstat.json", "w"))
    else:
        data = json.load(open("comstat.json"))

    if not data["areServicesAvailable"]:
        print("No services available.")
        return

    # TODO: warn if generatedAt is too old.
    # TODO: warn if generatedAt is too new.
    # TODO: warn if nrccMessages is not empty, and summarise the messages.

    if not data.get("trainServices", None):
        print("No train services available.")
        return

    for service in data["trainServices"]:
        stops_at_destination = False
        estimated_stop_time = None
        if service["isCancelled"]:
            continue
        for calling_point_list in service["subsequentCallingPoints"]:
            for calling_point in calling_point_list["callingPoint"]:
                if calling_point["crs"] == args.destination:
                    stops_at_destination = True
                    estimated_stop_time = (
                        calling_point["et"]
                        if calling_point["et"] != "On time"
                        else calling_point["st"]
                    )
        if not stops_at_destination:
            continue
        print(service)
        print("Estimated stop time:", estimated_stop_time)
        print(
            "Estimated departure time:",
            service["etd"] if service["etd"] != "On time" else service["std"],
        )


if __name__ == "__main__":
    main()
