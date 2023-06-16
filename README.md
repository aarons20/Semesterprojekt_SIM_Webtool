# SIM Profile Writer

This is a web application built with Python and Flask that allows users to write SIM profiles to SIM cards. It provides a user-friendly interface to configure and manage SIM profiles.

## Setup and Installation

1. Clone the repository:
```
git clone https://github.com/aarons20/Semesterprojekt_SIM_Webtool.git
```

2. Create and activate a virtual environment:
```
python3 -m venv .venv 
source .venv/bin/activate
```

3. Install the required dependencies:
```
p install -r requirements.txt
```

4. Configure the application settings:

Update the configuration file `config.py` with your desired settings, such as database connection details and API keys.

5. Run the application:
```
python app.py
```


The application will be accessible at `http://localhost:5000`.

## Usage

1. Open the web application in your browser.

2. Navigate to the SIM Profile section and create a new SIM profile by providing the necessary details.

3. Connect the SIM card writer device to your computer.

4. Insert a blank SIM card into the device.

5. Select the desired SIM profile from the web application and initiate the writing process.

6. Wait for the process to complete and verify the success message.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE. See the [LICENSE](LICENSE) file for more information.
