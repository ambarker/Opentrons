import csv

metadata = {
    'protocolName': 'Standardize DNA Concentrations',
    'author': 'AMB, last updated 3/23/22',
    'description': 'Adds designated amounts of DNA and water to wells in order to '
                   'standardize samples to a target concentration',
    'apiLevel': '2.11'
}

def run(protocol):

########## EDIT THESE RUN OPTIONS AS NEEDED ##########

    # location of p300 single channel ('left' or 'right', all lowercase and in single quotes)
    pipette_mount_300 = 'left'

    # location of p20 single channel ('left' or 'right', all lowercase and in single quotes)
    pipette_mount_20 = 'right'

    # number of source (DNA) plates (integar, min: 1 max: 3)
    num_source_plates = 3

    # number of destination (standardized) plates (integar, min: 1 max: 2)
    num_destination_plates = 2

    # sample standardization info
    # paste data from csv here (in between '''  ''')
    input_data = '''
    source_slot,source_well,dest_slot,dest_well,vol_dna,vol_water
    1,A1,1,A1,40,60
    1,C1,1,B1,66.67,33.33
    2,D1,2,C1,20,80
    3,E3,2,D1,10,90
    '''


########## DO NOT EDIT BELOW THIS LINE ##########

    # turn on lights if not on already
    protocol.set_rail_lights(True)

    # checks
    if pipette_mount_300 == pipette_mount_20:
        raise Exception('Invalid pipette placement')
    if pipette_mount_300 is None:
        raise Exception('Must attach single channel p300')
    if pipette_mount_20 is None:
        raise Exception("Must attach single channel p20")
    if num_source_plates < 1 or num_source_plates > 3:
        raise Exception("Invalid number of source plates. Must be 1-3")
    if num_destination_plates < 1 or num_destination_plates > 2:
        raise Exception("Invalid number of destination plates. Must be 1-2")

    # Define hardware, pipettes/tips, plates
    # load tips
    tips300 = [
     protocol.load_labware(
      'opentrons_96_tiprack_300ul', str(slot)) for slot in [
      7, 10, 11]]
    tips20 = [
     protocol.load_labware(
      'opentrons_96_filtertiprack_20ul', str(slot)) for slot in [
      8, 9]]
    # specify pipette, mount location, and tips
    p300 = protocol.load_instrument("p300_single_gen2", mount=pipette_mount_300, tip_racks=tips300)
    p20 = protocol.load_instrument("p20_single_gen2", mount=pipette_mount_20, tip_racks=tips20)

    # load reagent labware and specify reagents in each well/columns
    water_reservoir = protocol.load_labware(
        'nest_12_reservoir_15ml', '4')
    water = [water_reservoir.wells_by_name()[well] for well in ['A1']]

    # load plates
    # add first source DNA plate
    protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '1')
    #if more than one plate, add 2nd
    if num_source_plates > 1:
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '2')
    # if more than 2 plates, add 3rd
    if num_source_plates > 2:
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '3')
    # add first DNA destination plate
    protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5')
    # if more than one plate, add second
    if num_destination_plates > 1:
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6')

    # parse input data
    csv_data = [[val.strip() for val in line.split(',')]
                for line in input_data.splitlines()
                if line.split(',')[0].strip()][1:]

    # add water to all destination wells
    # first have both pipettes pick up tips
    p20.pick_up_tip()
    p300.pick_up_tip()
    # loops through wells and add water
    for row in csv_data:
        dest_well = protocol.loaded_labwares[int(row[2])].wells_by_name()[row[3]]
        vol_water = float(row[5])
        # use p20 if appropriate volume. Dispense at top of well so nothing touches and you can ues the same tip
        if 0 < vol_water <= 20:
            p20.transfer(vol_water, water, dest_well.top(1), blow_out=True,
                        blowout_location='destination well', new_tip='never')
        # use p300 if appropriate volume. Dispense at top of well so nothing touches and you can ues the same tip
        if vol_water > 20:
            p300.transfer(vol_water, water, dest_well.top(1), blow_out=True,
                        blowout_location='destination well', new_tip='never')
    # drop tips after all water has been added
    p20.drop_tip()
    p300.drop_tip()

    # add dna to each well
    for row in csv_data:
        source_well = protocol.loaded_labwares[int(row[0])].wells_by_name()[row[1]]
        dest_well = protocol.loaded_labwares[int(row[2])].wells_by_name()[row[3]]
        vol_dna = float(row[4])
        # use p20 if appropriate volume
        if 0 < vol_dna <= 20:
            p20.transfer(vol_dna, source_well, dest_well, blow_out=True,
                        blowout_location='destination well', new_tip='always')
        # use p300 if appropriate volume
        if vol_dna > 20:
            p300.transfer(vol_dna, source_well, dest_well, blow_out=True,
                        blowout_location='destination well', new_tip='always')

    # turn off lights
    protocol.set_rail_lights(False)
