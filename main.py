from database.database import initialize_database
from ui.main_window import create_main_window


def main():
    initialize_database()
    root = create_main_window()
    root.mainloop()


if __name__ == "__main__":
    main()
