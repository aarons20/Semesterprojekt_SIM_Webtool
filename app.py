import time
from flask import Flask, jsonify, render_template, request, abort
from database_connectivity import DataBaseConnectivity
from models.sim_profile import SIMProfile
from sim_reader_writer import SIMReaderWriter, SimReaderWriterStatus


app = Flask(__name__)
sim_reader_writer = SIMReaderWriter()
db = DataBaseConnectivity()

@app.route('/')
@app.route('/get-updated-profiles')
def index():
    profiles = None
    try:
        profiles = db.getSIMProfiles()
    except Exception as e:
        print(str(e))
        profiles = []
    active_imsi = None
    sim_profile = sim_reader_writer.get_sim_profile()
    """
    Debugging
    print(f"SIM-Profil: {sim_profile}")
    print("++++")
    print("SIMReaderWriter",
          sim_reader_writer.opts_reader, 
          sim_reader_writer.opts_writer,
          sim_reader_writer.sl,
          sim_reader_writer.card,
          sim_reader_writer.scc
          )
    print("++++")
    """
    if sim_profile is not None:       
        active_imsi = sim_profile.imsi
    reader_status = sim_reader_writer.reader_status()
    return render_template('index.html', 
                           profiles=profiles,
                           active_imsi = active_imsi, 
                           status = reader_status,
                           SimReaderWriterStatus=SimReaderWriterStatus)

@app.route('/write-sim-profile', methods=['POST'])
def trigger_method():
    print(" ======= Running request...")
    imsi = request.form.get('imsi')
    print("Received imsi:", imsi)
    sim_profiles = db.getSIMProfiles()

    # Find the SIMProfile object with the matching 'imsi'
    target_profile = None
    for profile in sim_profiles:
        if profile.imsi == imsi:
            target_profile = profile
            break

    # Try to write sim profile if profile found
    trys_for_writing = 3
    if target_profile:        
        while(trys_for_writing > 0):       
            try:   
                sim_reader_writer.write_sim(sim_profile=target_profile)
                break
            except Exception as e:
                print("--- In except writing")          
                if(trys_for_writing > 0):
                    time.sleep(1)
                    trys_for_writing -= 1                    
                else:
                    abort(400, "Error: " + str(e))
    else:
        # The target_profile is not found
        abort(400, "Error: SIMProfile not found")

    return 'SIM updated successfully'

@app.route('/create-sim-profile', methods=['POST'])
def create_sim_profile():
    name = request.form.get('name')
    imsi = request.form.get('imsi')
    ki = request.form.get('ki')
    opc = request.form.get('opc')
    print(f"imsi {imsi}, name {name} ki {ki} opc {opc}")

    sim_profile = SIMProfile(        
                imsi=imsi,
                name=name,
                ki=ki,
                opc=opc
            )
    try:
        db.addSIMProfile(sim_profile=sim_profile)
        return 'Success'
    except Exception as e:
        abort(400, str(e))

@app.errorhandler(400)
def handle_bad_request(error):
    response = jsonify(message=error.description)
    response.status_code = error.code
    return response

if __name__ == '__main__':
    app.run(debug=True)
