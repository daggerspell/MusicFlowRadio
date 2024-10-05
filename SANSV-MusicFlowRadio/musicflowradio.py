from . import AIRadioStation


class RadioStationUI:
    def __init__(self, station: AIRadioStation):
        self.station = station

    def run(self):
        while True:
            print("\nDagger Spell FM Management Console")
            print("1. Add Song")
            print("2. Remove Song")
            print("3. Add Commercial")
            print("4. Start Radio")
            print("5. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                file_path = input("Enter file path: ")
                self.station.add_song(file_path)
            elif choice == "2":
                title = input("Enter song title to remove: ")
                self.station.remove_song(title)
            elif choice == "3":
                name = input("Enter commercial name: ")
                file_path = input("Enter file path: ")
                self.station.add_commercial(name, file_path)
            elif choice == "4":
                print("Starting radio station...")
                self.station.run_station()
            elif choice == "5":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    radio = AIRadioStation()
    ui = RadioStationUI(radio)
    ui.run()
