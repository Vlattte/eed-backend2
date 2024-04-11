import json
import os

def GetInstruction(app, step_id): #app - название аппаратура, step_id - номер шага
    print("[step_id]", step_id)
    project_path = os.path.abspath(__file__ + "/..")
    print(f'instruction_path: {project_path + "/" + app}')
    instr_file = open(project_path + "/" + app, encoding='utf-8')
    data = json.load(instr_file)
    instr_file.close()

    for i in range(len(data)):
        if data["step_"+str(i)]["step"] == step_id:
            return data["step_"+str(i)]
