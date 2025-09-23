# Apprentice Toolkit 

The **Apprentice Toolkit** was born quite casually: the initial idea was simply to eliminate the need to use Excel’s `TEXTJOIN` formula. At first, it was just a small script to make everyday work easier. But, like every project that solves a real pain point, it started to grow. After receiving positive feedback from colleagues, I realized it could go much further: I began automating other workflows, adding new features, and soon the original name no longer made sense. It might be difficult to understand what this program actually does, since its use cases are extremely specific and niche, but it has truly been helping me a lot recently.

Originally created to be the final project for **CS50P** (and to be honest, it’s not even finished yet). 

---

## Key Features

Currently, the toolkit offers several functions to streamline repetitive and tedious office tasks. Some highlights include:

- **Work Order Processing** (`process_orders`)  
  Automatically formats service orders by inserting separators every 8 characters. Goodbye, manual copy-and-paste in Excel.

- **Text Manipulation** (`process_text`)  
  Converts text blocks into lists separated by commas, semicolons, or any chosen separator. Also lets you decide whether to keep or replace spaces.

- **Work Log Management** (`work_logs`)  
  Insert the service order, date, and time range, and it automatically generates logs with start/end times and even calculates the actual hours worked (even if a bit unrealistic, lol).

- **Order Search** (`search_orders`)  
  Extracts only valid order numbers (pattern `621xxxxx`) from any text and displays the total found.

- **Maintenance Plan Integration** (`get_equipment_and_plan`, `fetch_plans`)  
  Loads CSV files with maintenance matrices and service orders, cross-referencing them to identify equipment, valid plans, and generate task lists.  
  *(Since I cannot provide personal data about the place where I work, this part — along with the automatic work log generation — should be considered obsolete for third-party users. Because of that, I will adapt it so that it no longer requires the CSV files it would normally need in this redistribution.)*

- **Tire Service Separation** (`split_tire_service`)  
  Automatically separates tire-related tasks from mechanical services, making maintenance sequences easier to organize and enabling automatic work log generation.

- **Quick Copy of Results** (`copy_text`)  
  Allows users to copy generated output directly to the clipboard with a single click.

---

## Graphical Interface

The project uses **Tkinter** to provide a simple but functional graphical interface. This way, users can interact with the toolkit without editing code or running terminal commands, making it accessible to my coworkers and anyone else who doesn’t know programming.

---

## Testing

Unit tests were implemented with `pytest`, using mock objects to simulate text input, output boxes, and labels. This ensures that critical functions such as `process_orders`, `process_text`, and `search_orders` behave reliably.


