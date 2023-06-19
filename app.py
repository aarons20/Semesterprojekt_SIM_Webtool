from flask import Flask, render_template, request
from database_connectivity import DataBaseConnectivity
from models.sim_profile import SIMProfile
from sim_reader_writer import SIMReaderWriter, SimReaderWriterStatus


app = Flask(__name__)
sim_reader_writer = SIMReaderWriter()
db = DataBaseConnectivity()

@app.route('/')
@app.route('/get-updated-profiles')
def index():
    profiles = db.getSIMProfiles()
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

    # Check if the target_profile was found
    if target_profile:
        try:
            sim_reader_writer.write_sim(sim_profile=target_profile)
        except:
            return "Error occured"
    else:
        # The target_profile is not found
        print('SIMProfile not found')

    return 'Method triggered successfully'

if __name__ == '__main__':
    app.run(debug=True)
