# Data Structures Web App

## Project summary
This project is a web application to help users learn and test their knowledge of data structures. It includes features like quizzes, leaderboards, and visualizations.

## Settting up
1. Clone the repository:<br>
   git clone https://github.com/acastro23/ds-webapp.git<br>
   cd ds_webapp


2. Create and activate a virtual environment like this:
   <i>python -m venv dsENV</i>
   - **Windows**: .\dsENV\Scripts\Activate
   - **macOS/Linux**: source dsENV/bin/activate (not tested, but just in case)


3. Install dependencies through this comand:
   <i>pip install -r requirements.txt</i>


4. Create a `.env` file in the project directory and add this stuff:<br>
   DB_NAME=postgres<br>
   DB_USER=postgres<br>
   DB_PASSWORD=FpOHwr9qjcryoiyl<br>
   DB_HOST=db.frpyyycywlsdoctjwcag.supabase.co<br>
   DB_PORT=5432<br>
   SUPABASE_URL=https://frpyyycywlsdoctjwcag.supabase.co<br>
   SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZycHl5eWN5d2xzZG9jdGp3Y2FnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTYxODM0MiwiZXhwIjoyMDUxMTk0MzQyfQ.AV-_oCpnIEWbJSv9-9laBJvDXo4pwVTxw9pZlSlSMmQ   


5. run this command:
   python manage.py migrate


6. Run the server with this command:
   <i>python manage.py runserver</i><br>
   check the app at http://127.0.0.1:8000/