1. 
2. before testing started, make sure the api are running by using docker compose.
3. If docker compose not possible, try to run development build without docker.
```
  cd server
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/appdb"
  python run.py
```
4. DO NOT USE ANY MOCKUP DATA, instead use real data provided.
5. The real xml data located at `/oldparser/cc.xml`
6. The old logic for xml parsing all located in the `/oldparser`
7. all the database are empty, please fill the database by uploading the project repository XML `/oldparser/cc.xml` and upload it into database by using `/xml-parser` function in the webapp.
8. make sure debugging should be following from problem statement then try to replciate the bug. 
9. Before ending you session, test all the asked/provided request using playwright (not the unit testing in this project) tool from your MCP
