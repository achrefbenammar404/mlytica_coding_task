from fastapi import FastAPI, HTTPException
from common.data_manager import DataManager

app = FastAPI()
data_manager = DataManager()

@app.get("/get_department/{placement}")
def get_department(placement: str):
    results = data_manager.read_competition_results()
    if placement in results:
        return {"department": results[placement]['department']}
    else:
        #raise HTTPException(status_code=404, detail="Placement not found")
        return 'shiiiiiit'

@app.get("/get_employee/{placement}")
def get_employee(placement: str):
    results = data_manager.read_competition_results()
    if placement in results:
        return {"employee": results[placement]['employee']}
    else:
        raise HTTPException(status_code=404, detail="Placement not found")
