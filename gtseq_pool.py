# one pcr plate worth of samples half skirt inserted into alumninum block or green skirt plate
# into 1.5 ml tube

metadata = {
    'protocolName': 'GTSeq pool ',
    'author': 'AMB, last updated 4/18/22',
    'description': 'Pool GT seq samples (variable volumes) into one tube.',
    'apiLevel': '2.11'
}

def run(protocol):
    ########## EDIT THESE RUN OPTIONS AS NEEDED ##########

    # location of p20 single channel ('left' or 'right', all lowercase and in single quotes)
    pipette_mount_20 = 'right'

    # number of plates (integar, max 9)
    num_plates = 3

    # sample volume info
    # paste data from csv here (in between '''  ''')
    input_data = '''
    source_slot,source_well,tube_well,vol_dna
    3,A1,A1,1
    3,A2,A1,2
    3,A3,A1,3
    3,A4,A1,4
    3,A5,A1,5
    3,A6,A1,6
    3,A7,A1,7
    3,A8,A1,8
    3,A9,A1,9
    3,A10,A1,10
    3,A11,A1,10
    3,A12,A1,9
    4,A1,A2,8
    4,A2,A2,7
    4,A3,A2,6
    4,A4,A2,5
    4,A5,A2,4
    4,A6,A2,3
    5,A1,B1,2
    5,A2,B1,1
    5,A3,B1,10
    5,A4,B1,10
    5,A5,B1,10
    5,A6,B1,10
    '''

    ########## DO NOT EDIT BELOW THIS LINE ##########

    # turn on lights if not on already
    protocol.set_rail_lights(True)

    # checks
    if pipette_mount_20 is None:
        raise Exception("Must attach single channel p20")

    # Define hardware, pipettes/tips, plates
    # load tips
    tips20 = [protocol.load_labware(
            'opentrons_96_tiprack_20ul', str(slot)) for slot in [
            2]]

    # specify pipette, mount location, and tips
    p20 = protocol.load_instrument("p20_single_gen2", mount=pipette_mount_20, tip_racks=tips20)

    # load reagent labware and specify reagents in each well/columns
    tube_rack = protocol.load_labware('opentrons_24_aluminumblock_nest_1.5ml_snapcap', 1)

    # load plates
    slot_range = list(range(3, 3 + num_plates))
    [protocol.load_labware('vwr_96_wellplate_200ul_greenplate', str(slot)) for slot in slot_range]

    # parse input data
    csv_data = [[val.strip() for val in line.split(',')]
                for line in input_data.splitlines()
                if line.split(',')[0].strip()][1:]

    # set aspirate and dispense speeds
    p20.flow_rate.aspirate = 150
    p20.flow_rate.dispense = 150


    p20.pick_up_tip()
    # set starting tube
    current_tube = 'A1'
    # add dna to tube
    for row in csv_data:
        source_well = protocol.loaded_labwares[int(row[0])].wells_by_name()[row[1]]
        dest_tube = tube_rack.wells_by_name()[row[2]]
        vol_dna = float(row[3])
        vol_dna = round(vol_dna, 2)
        # if the new destination tube isnt the same as what the previous run, change tips
        if row[2] != current_tube:
            p20.drop_tip()
            p20.pick_up_tip()
        # check volume
        if vol_dna < 1.0 or vol_dna > 20.0:
            raise Exception("Invalid volume of dna. Must be between 1.0-20.0")
        # round to 2 decimal places
        vol_dna = round(vol_dna, 2)
        p20.transfer(vol_dna, source_well, dest_tube, blow_out=True,
                         blowout_location='destination well', touch_tip=True, new_tip='never')
        # update current tube to compare on next round
        current_tube = row[2]

    p20.drop_tip()

    ### make sure the tube checking thing works ###

    # turn off lights
    protocol.set_rail_lights(False)


